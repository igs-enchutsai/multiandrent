// Package api provides the REST API server for cross-agent communication.
package api

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"

	"kiro-multi-agent/internal/daemon"
	"kiro-multi-agent/internal/telegram"
)

// Server is the HTTP API server.
type Server struct {
	daemon   *daemon.Daemon
	telegram *telegram.Adapter
	listener net.Listener
}

// New creates a new API server.
func New(d *daemon.Daemon, tg *telegram.Adapter) *Server {
	return &Server{
		daemon:   d,
		telegram: tg,
	}
}

// Start starts the HTTP server on the given port.
func (s *Server) Start(port int) error {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /api/status", s.handleStatus)
	mux.HandleFunc("POST /api/send", s.handleSend)
	mux.HandleFunc("POST /api/reply", s.handleReply)
	mux.HandleFunc("POST /api/reply/photo", s.handleReplyPhoto)
	mux.HandleFunc("POST /api/reply/document", s.handleReplyDocument)
	mux.HandleFunc("POST /api/log", s.handleLog)
	mux.HandleFunc("POST /api/progress", s.handleProgress)

	addr := fmt.Sprintf("127.0.0.1:%d", port)
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		return fmt.Errorf("API 監聽失敗: %w", err)
	}
	s.listener = ln

	go func() {
		if err := http.Serve(ln, mux); err != nil && err != http.ErrServerClosed {
			log.Printf("[api] 伺服器錯誤: %v", err)
		}
	}()

	log.Printf("[api] 已啟動於 %s", addr)
	return nil
}

// Stop stops the HTTP server.
func (s *Server) Stop() {
	if s.listener != nil {
		s.listener.Close()
	}
}

func (s *Server) handleStatus(w http.ResponseWriter, r *http.Request) {
	status := s.daemon.GetStatus()
	writeJSON(w, map[string]interface{}{
		"ok":        true,
		"instances": status,
	})
}

type sendRequest struct {
	Instance string `json:"instance"`
	Message  string `json:"message"`
	Source   string `json:"source"`
}

func (s *Server) handleSend(w http.ResponseWriter, r *http.Request) {
	var req sendRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "invalid request"})
		return
	}

	response, err := s.daemon.SendMessage(req.Instance, req.Message)
	if err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": err.Error()})
		return
	}
	writeJSON(w, map[string]interface{}{"ok": true, "response": response})
}

type replyRequest struct {
	Instance string `json:"instance"`
	Text     string `json:"text"`
	Kind     string `json:"kind"`
}

func (s *Server) handleReply(w http.ResponseWriter, r *http.Request) {
	var req replyRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "invalid request"})
		return
	}

	if s.telegram != nil {
		ok := s.telegram.SendText(req.Instance, req.Text)
		writeJSON(w, map[string]interface{}{"ok": ok})
	} else {
		log.Printf("[api] [reply] %s: %s", req.Instance, truncate(req.Text, 100))
		writeJSON(w, map[string]interface{}{"ok": true})
	}
}

type photoRequest struct {
	Instance  string `json:"instance"`
	PhotoPath string `json:"photo_path"`
	Caption   string `json:"caption"`
}

func (s *Server) handleReplyPhoto(w http.ResponseWriter, r *http.Request) {
	var req photoRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "invalid request"})
		return
	}

	if s.telegram != nil {
		ok := s.telegram.SendPhoto(req.Instance, req.PhotoPath, req.Caption)
		writeJSON(w, map[string]interface{}{"ok": ok})
	} else {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "Telegram not connected"})
	}
}

type documentRequest struct {
	Instance string `json:"instance"`
	FilePath string `json:"file_path"`
	Caption  string `json:"caption"`
}

func (s *Server) handleReplyDocument(w http.ResponseWriter, r *http.Request) {
	var req documentRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "invalid request"})
		return
	}

	if s.telegram != nil {
		ok := s.telegram.SendDocument(req.Instance, req.FilePath, req.Caption)
		writeJSON(w, map[string]interface{}{"ok": ok})
	} else {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "Telegram not connected"})
	}
}

type logRequest struct {
	Instance string `json:"instance"`
	Text     string `json:"text"`
}

func (s *Server) handleLog(w http.ResponseWriter, r *http.Request) {
	var req logRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "invalid request"})
		return
	}

	log.Printf("[log] %s: %s", req.Instance, truncate(req.Text, 200))
	writeJSON(w, map[string]interface{}{"ok": true})
}

func (s *Server) handleProgress(w http.ResponseWriter, r *http.Request) {
	var req map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, map[string]interface{}{"ok": false, "error": "invalid request"})
		return
	}

	log.Printf("[progress] %v: %v", req["instance"], req["message"])
	writeJSON(w, map[string]interface{}{"ok": true})
}

func writeJSON(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
