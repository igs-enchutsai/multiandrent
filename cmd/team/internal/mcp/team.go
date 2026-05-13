// Package mcp provides stdio JSON-RPC MCP servers for team communication.
package mcp

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// TeamServer is the Team MCP server providing cross-agent communication tools.
type TeamServer struct {
	Port     int
	Instance string
	Role     string
}

// jsonRPCRequest represents a JSON-RPC 2.0 request.
type jsonRPCRequest struct {
	JSONRPC string                 `json:"jsonrpc"`
	ID      interface{}            `json:"id,omitempty"`
	Method  string                 `json:"method"`
	Params  map[string]interface{} `json:"params,omitempty"`
}

// jsonRPCResponse represents a JSON-RPC 2.0 response.
type jsonRPCResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      interface{} `json:"id,omitempty"`
	Result  interface{} `json:"result,omitempty"`
	Error   interface{} `json:"error,omitempty"`
}

var teamTools = []map[string]interface{}{
	{
		"name":        "reply",
		"description": "Reply to user via Telegram.",
		"inputSchema": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"text": map[string]interface{}{"type": "string"},
				"kind": map[string]interface{}{"type": "string", "enum": []string{"primary", "followup"}, "default": "primary"},
			},
			"required": []string{"text"},
		},
	},
	{
		"name":        "query_team_status",
		"description": "Query team agent status.",
		"inputSchema": map[string]interface{}{
			"type":       "object",
			"properties": map[string]interface{}{},
		},
	},
	{
		"name":        "log_to_leader",
		"description": "Send internal message to leader (not visible to user).",
		"inputSchema": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"text": map[string]interface{}{"type": "string"},
			},
			"required": []string{"text"},
		},
	},
	{
		"name":        "report_progress",
		"description": "Report task progress.",
		"inputSchema": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"message": map[string]interface{}{"type": "string"},
			},
			"required": []string{"message"},
		},
	},
	{
		"name":        "record_spend",
		"description": "Record API spend for cost tracking.",
		"inputSchema": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"amount_usd": map[string]interface{}{"type": "number"},
			},
			"required": []string{"amount_usd"},
		},
	},
	{
		"name":        "send_to_instance",
		"description": "Send message to another agent (leader only).",
		"inputSchema": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"instance": map[string]interface{}{"type": "string"},
				"message":  map[string]interface{}{"type": "string"},
			},
			"required": []string{"instance", "message"},
		},
	},
}

// Run starts the Team MCP server on stdio.
func (s *TeamServer) Run() {
	log.SetOutput(os.Stderr)
	log.Printf("Team MCP Server started (instance=%s, role=%s)", s.Instance, s.Role)

	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 1024*1024), 1024*1024)

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}

		var req jsonRPCRequest
		if err := json.Unmarshal([]byte(line), &req); err != nil {
			continue
		}

		resp := s.handleRequest(req)
		if resp != nil {
			data, _ := json.Marshal(resp)
			fmt.Fprintf(os.Stdout, "%s\n", data)
		}
	}
}

func (s *TeamServer) handleRequest(req jsonRPCRequest) *jsonRPCResponse {
	switch req.Method {
	case "initialize":
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result: map[string]interface{}{
				"protocolVersion": "2024-11-05",
				"capabilities":    map[string]interface{}{"tools": map[string]interface{}{"listChanged": false}},
				"serverInfo":      map[string]interface{}{"name": "team-mcp", "version": "1.0.0"},
			},
		}

	case "notifications/initialized":
		return nil

	case "tools/list":
		tools := teamTools
		if s.Role != "leader" {
			// Filter out send_to_instance for non-leaders
			var filtered []map[string]interface{}
			for _, t := range teamTools {
				if t["name"] != "send_to_instance" {
					filtered = append(filtered, t)
				}
			}
			tools = filtered
		}
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result:  map[string]interface{}{"tools": tools},
		}

	case "tools/call":
		toolName, _ := req.Params["name"].(string)
		arguments, _ := req.Params["arguments"].(map[string]interface{})
		if arguments == nil {
			arguments = map[string]interface{}{}
		}
		result := s.handleTool(toolName, arguments)
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result: map[string]interface{}{
				"content": []map[string]interface{}{{"type": "text", "text": result}},
			},
		}

	default:
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Error:   map[string]interface{}{"code": -32601, "message": fmt.Sprintf("Unknown: %s", req.Method)},
		}
	}
}

func (s *TeamServer) handleTool(name string, args map[string]interface{}) string {
	switch name {
	case "reply":
		text, _ := args["text"].(string)
		kind, _ := args["kind"].(string)
		if kind == "" {
			kind = "primary"
		}
		r := s.apiCall("POST", "/api/reply", map[string]interface{}{
			"instance": s.Instance, "text": text, "kind": kind,
		})
		if r["ok"] == true {
			return "sent"
		}
		return fmt.Sprintf("failed: %v", r)

	case "query_team_status":
		r := s.apiCall("GET", "/api/status", nil)
		instances, _ := r["instances"].([]interface{})
		var lines []string
		for _, inst := range instances {
			m, _ := inst.(map[string]interface{})
			status, _ := m["status"].(string)
			n, _ := m["name"].(string)
			icon := map[string]string{"running": "G", "stopped": "W", "crashed": "R"}[status]
			if icon == "" {
				icon = "?"
			}
			lines = append(lines, fmt.Sprintf("[%s] %s - %s", icon, n, status))
		}
		if len(lines) == 0 {
			return "no instances"
		}
		return strings.Join(lines, "\n")

	case "log_to_leader":
		text, _ := args["text"].(string)
		s.apiCall("POST", "/api/log", map[string]interface{}{
			"instance": s.Instance, "text": text,
		})
		return "logged"

	case "send_to_instance":
		if s.Role != "leader" {
			return "permission denied: only leader can send"
		}
		instance, _ := args["instance"].(string)
		message, _ := args["message"].(string)
		r := s.apiCall("POST", "/api/send", map[string]interface{}{
			"instance": instance, "message": message, "source": s.Instance,
		})
		if r["ok"] == true {
			return "sent"
		}
		return fmt.Sprintf("failed: %v", r)

	case "report_progress":
		message, _ := args["message"].(string)
		s.apiCall("POST", "/api/progress", map[string]interface{}{
			"instance": s.Instance, "message": message,
		})
		return "progress updated"

	case "record_spend":
		amountUSD, _ := args["amount_usd"].(float64)
		r := s.apiCall("POST", "/api/costs/spend", map[string]interface{}{
			"instance": s.Instance, "amount_usd": amountUSD,
		})
		if r["ok"] == true {
			return "recorded"
		}
		return fmt.Sprintf("failed: %v", r)

	default:
		return fmt.Sprintf("unknown tool: %s", name)
	}
}

func (s *TeamServer) apiCall(method string, path string, data map[string]interface{}) map[string]interface{} {
	url := fmt.Sprintf("http://127.0.0.1:%d%s", s.Port, path)

	var body io.Reader
	if data != nil {
		jsonData, _ := json.Marshal(data)
		body = bytes.NewReader(jsonData)
	}

	maxRetries := 3
	for attempt := 0; attempt <= maxRetries; attempt++ {
		req, err := http.NewRequest(method, url, body)
		if err != nil {
			continue
		}
		if data != nil {
			req.Header.Set("Content-Type", "application/json")
		}

		client := &http.Client{Timeout: 10 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			if attempt < maxRetries {
				time.Sleep(time.Duration(500*(1<<attempt)) * time.Millisecond)
				// Reset body for retry
				if data != nil {
					jsonData, _ := json.Marshal(data)
					body = bytes.NewReader(jsonData)
				}
				continue
			}
			return map[string]interface{}{"ok": false, "error": "API unreachable"}
		}
		defer resp.Body.Close()

		var result map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&result)
		return result
	}

	return map[string]interface{}{"ok": false, "error": "API unreachable"}
}
