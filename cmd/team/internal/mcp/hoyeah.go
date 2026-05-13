package mcp

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// HoYeahServer is the HoYeah API MCP server providing query_hoyeah tool.
type HoYeahServer struct{}

var hoyeahTools = []map[string]interface{}{
	{
		"name":        "query_hoyeah",
		"description": "查詢營運數據。直接用自然語言提問，例如：'CN今天營收多少'、'昨天全服DAU'、'本週付費率趨勢'",
		"inputSchema": map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"question": map[string]interface{}{
					"type":        "string",
					"description": "自然語言查詢問題",
				},
			},
			"required": []string{"question"},
		},
	},
}

// Run starts the HoYeah MCP server on stdio.
func (s *HoYeahServer) Run() {
	log.SetOutput(os.Stderr)
	log.Println("HoYeah MCP Server started")

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

func (s *HoYeahServer) handleRequest(req jsonRPCRequest) *jsonRPCResponse {
	switch req.Method {
	case "initialize":
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result: map[string]interface{}{
				"protocolVersion": "2024-11-05",
				"capabilities":    map[string]interface{}{"tools": map[string]interface{}{}},
				"serverInfo":      map[string]interface{}{"name": "hoyeah-api", "version": "1.0.0"},
			},
		}

	case "notifications/initialized":
		return nil

	case "tools/list":
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result:  map[string]interface{}{"tools": hoyeahTools},
		}

	case "tools/call":
		toolName, _ := req.Params["name"].(string)
		arguments, _ := req.Params["arguments"].(map[string]interface{})
		if arguments == nil {
			arguments = map[string]interface{}{}
		}

		if toolName == "query_hoyeah" {
			question, _ := arguments["question"].(string)
			var content string
			if question == "" {
				content = "錯誤：請提供查詢問題"
			} else {
				content = queryHoYeah(question)
			}
			return &jsonRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Result: map[string]interface{}{
					"content": []map[string]interface{}{{"type": "text", "text": content}},
					"isError": false,
				},
			}
		}

		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Error:   map[string]interface{}{"code": -32601, "message": fmt.Sprintf("Unknown tool: %s", toolName)},
		}

	default:
		return &jsonRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Error:   map[string]interface{}{"code": -32601, "message": fmt.Sprintf("Unknown method: %s", req.Method)},
		}
	}
}

func queryHoYeah(question string) string {
	apiBase := os.Getenv("HOYEAH_API_BASE")
	if apiBase == "" {
		return "錯誤：未設定 HOYEAH_API_BASE 環境變數，請在 .env 中設定"
	}
	apiKey := os.Getenv("HOYEAH_API_KEY")

	url := strings.TrimRight(apiBase, "/") + "/chat/completions"

	payload := map[string]interface{}{
		"model": "hermes-agent",
		"messages": []map[string]interface{}{
			{"role": "user", "content": question},
		},
	}

	jsonData, _ := json.Marshal(payload)

	req, err := http.NewRequest("POST", url, bytes.NewReader(jsonData))
	if err != nil {
		return fmt.Sprintf("錯誤：%v", err)
	}
	req.Header.Set("Content-Type", "application/json")
	if apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+apiKey)
	}

	client := &http.Client{Timeout: 600 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		if os.IsTimeout(err) {
			return "錯誤：API 請求超時（600秒）"
		}
		return fmt.Sprintf("錯誤：無法連線到 HoYeah API - %v", err)
	}
	defer resp.Body.Close()

	var result struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Sprintf("錯誤：解析回應失敗 - %v", err)
	}

	if len(result.Choices) > 0 {
		return result.Choices[0].Message.Content
	}
	return "API 回覆為空"
}
