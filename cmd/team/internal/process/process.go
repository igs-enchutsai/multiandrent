// Package process manages kiro-cli as a subprocess with stdin/stdout pipes.
package process

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"sync"
	"time"
)

const (
	maxCaptureLines = 5000
	responseTimeout = 15 * time.Minute
	timeoutMessage  = "⏱️ 搜尋超時（超過 15 分鐘），請稍後再試或換個問法。"
)

var (
	// ANSI escape sequences
	ansiRegex    = regexp.MustCompile(`\x1b\[[0-9;]*[a-zA-Z]`)
	ansiQRegex   = regexp.MustCompile(`\x1b\[\?[0-9;]*[a-zA-Z]`)
	spinnerRegex = regexp.MustCompile(`[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]\s*\w+\.\.\.`)
	brailleRegex = regexp.MustCompile(`^[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]+\s*`)
	multiSpace   = regexp.MustCompile(`  +`)
)

// skipPatterns are lines to filter from kiro-cli output when extracting responses.
var skipPatterns = []string{
	"▸ Time:", "╭─", "╰─", "│", "Model:",
	"Did you know?", "/context", "/model",
	"All tools are now trusted",
	"ask a question",
	"Thinking...", "Working...",
	"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏",
	"[?25", "[?12",
	"Running tool", "using tool:",
	"Completed in", "- Completed",
	"Successfully read", "Reading file:",
	"Reading directory:", "Querying available",
	"I will run the following command:",
	"Purpose:", "max depth:", "max entries:",
	"(from mcp server:",
	"⋮", "with the param",
}

// ManagedProcess wraps a kiro-cli subprocess with stdin/stdout access.
type ManagedProcess struct {
	Name string

	cmd    *exec.Cmd
	stdin  io.WriteCloser
	stdout io.ReadCloser

	mu           sync.Mutex
	outputLines  []string
	pendingResp  []string
	collecting   bool
	responseCh   chan string
}

// Start launches the kiro-cli subprocess.
func (mp *ManagedProcess) Start(command string, cwd string) error {
	// Parse command into executable and arguments
	parts := parseCommand(command)
	if len(parts) == 0 {
		return fmt.Errorf("空命令")
	}

	cmd := exec.Command(parts[0], parts[1:]...)
	cmd.Dir = cwd
	cmd.Env = append(os.Environ(), "PYTHONUTF8=1", "PYTHONIOENCODING=utf-8")

	stdinPipe, err := cmd.StdinPipe()
	if err != nil {
		return fmt.Errorf("建立 stdin pipe 失敗: %w", err)
	}
	stdoutPipe, err := cmd.StdoutPipe()
	if err != nil {
		return fmt.Errorf("建立 stdout pipe 失敗: %w", err)
	}
	cmd.Stderr = cmd.Stdout // merge stderr into stdout

	if err := cmd.Start(); err != nil {
		return fmt.Errorf("啟動程序失敗: %w", err)
	}

	mp.cmd = cmd
	mp.stdin = stdinPipe
	mp.stdout = stdoutPipe
	mp.outputLines = make([]string, 0, 256)
	mp.pendingResp = make([]string, 0, 256)
	mp.responseCh = make(chan string, 1)

	go mp.readOutput()

	log.Printf("[process] %s 已啟動 (pid=%d)", mp.Name, cmd.Process.Pid)
	return nil
}

// readOutput reads stdout in chunks (not line-by-line) to handle \r TUI updates.
func (mp *ManagedProcess) readOutput() {
	reader := bufio.NewReaderSize(mp.stdout, 8192)
	buf := make([]byte, 4096)

	var remainder string

	for {
		n, err := reader.Read(buf)
		if n > 0 {
			text := remainder + string(buf[:n])
			remainder = ""

			// Split on newlines and carriage returns
			for len(text) > 0 {
				nlIdx := strings.IndexByte(text, '\n')
				crIdx := strings.IndexByte(text, '\r')

				var pos int
				if nlIdx == -1 && crIdx == -1 {
					// No line break found, save as remainder
					remainder = text
					break
				} else if nlIdx == -1 {
					pos = crIdx
				} else if crIdx == -1 {
					pos = nlIdx
				} else {
					if nlIdx < crIdx {
						pos = nlIdx
					} else {
						pos = crIdx
					}
				}

				line := strings.TrimRight(text[:pos], " \t")
				text = text[pos+1:]

				if line == "" {
					continue
				}

				clean := StripANSI(line)
				if clean == "" {
					continue
				}

				mp.mu.Lock()
				mp.outputLines = append(mp.outputLines, clean)
				if len(mp.outputLines) > maxCaptureLines {
					mp.outputLines = mp.outputLines[len(mp.outputLines)-maxCaptureLines:]
				}
				if mp.collecting {
					mp.pendingResp = append(mp.pendingResp, clean)
					// Check for response completion marker
					if strings.Contains(clean, "▸ Time:") || strings.Contains(clean, "Time:") {
						response := mp.extractFinalResponse(mp.pendingResp)
						mp.pendingResp = mp.pendingResp[:0]
						mp.collecting = false
						mp.mu.Unlock()
						// Non-blocking send
						select {
						case mp.responseCh <- response:
						default:
						}
						continue
					}
				}
				mp.mu.Unlock()
			}
		}
		if err != nil {
			// Flush remainder
			if remainder != "" {
				clean := StripANSI(strings.TrimSpace(remainder))
				if clean != "" {
					mp.mu.Lock()
					mp.outputLines = append(mp.outputLines, clean)
					if mp.collecting {
						mp.pendingResp = append(mp.pendingResp, clean)
					}
					mp.mu.Unlock()
				}
			}
			break
		}
	}
}

// SendInput writes text to the subprocess stdin.
func (mp *ManagedProcess) SendInput(text string) error {
	if mp.stdin == nil {
		return fmt.Errorf("程序 %s 沒有 stdin", mp.Name)
	}

	mp.mu.Lock()
	mp.pendingResp = mp.pendingResp[:0]
	mp.collecting = true
	// Drain any old response
	select {
	case <-mp.responseCh:
	default:
	}
	mp.mu.Unlock()

	_, err := fmt.Fprintf(mp.stdin, "%s\n", text)
	return err
}

// WaitResponse waits for the response to complete (sees "▸ Time:" marker).
// Times out after 15 minutes.
func (mp *ManagedProcess) WaitResponse() string {
	select {
	case resp := <-mp.responseCh:
		return resp
	case <-time.After(responseTimeout):
		mp.mu.Lock()
		lines := make([]string, len(mp.pendingResp))
		copy(lines, mp.pendingResp)
		mp.pendingResp = mp.pendingResp[:0]
		mp.collecting = false
		mp.mu.Unlock()

		if len(lines) > 0 {
			return mp.extractFinalResponse(lines)
		}
		return timeoutMessage
	}
}

// Capture returns the last N lines of output.
func (mp *ManagedProcess) Capture(lines int) string {
	mp.mu.Lock()
	defer mp.mu.Unlock()

	if lines <= 0 || lines > len(mp.outputLines) {
		lines = len(mp.outputLines)
	}
	start := len(mp.outputLines) - lines
	if start < 0 {
		start = 0
	}
	return strings.Join(mp.outputLines[start:], "\n")
}

// IsAlive checks if the subprocess is still running.
func (mp *ManagedProcess) IsAlive() bool {
	if mp.cmd == nil || mp.cmd.Process == nil {
		return false
	}
	// On Unix, check if process exists; on Windows, ProcessState is nil if running
	if mp.cmd.ProcessState != nil {
		return false
	}
	return true
}

// PID returns the process ID.
func (mp *ManagedProcess) PID() int {
	if mp.cmd != nil && mp.cmd.Process != nil {
		return mp.cmd.Process.Pid
	}
	return 0
}

// Kill terminates the subprocess.
func (mp *ManagedProcess) Kill() {
	if mp.stdin != nil {
		mp.stdin.Close()
	}
	if mp.cmd != nil && mp.cmd.Process != nil {
		mp.cmd.Process.Kill()
		mp.cmd.Wait()
	}
}

// StripANSI removes ANSI escape sequences, terminal control codes, and spinner animations.
func StripANSI(text string) string {
	text = ansiRegex.ReplaceAllString(text, "")
	text = ansiQRegex.ReplaceAllString(text, "")
	text = spinnerRegex.ReplaceAllString(text, "")
	text = brailleRegex.ReplaceAllString(text, "")
	text = multiSpace.ReplaceAllString(text, " ")
	return strings.TrimSpace(text)
}

// extractFinalResponse filters kiro-cli output noise and returns the final answer.
func (mp *ManagedProcess) extractFinalResponse(responseLines []string) string {
	var responseBlocks []string
	var currentBlock []string
	inResponse := false

	for _, line := range responseLines {
		// Skip UI noise
		if containsAny(line, skipPatterns) {
			if inResponse && len(currentBlock) > 0 {
				responseBlocks = append(responseBlocks, strings.Join(currentBlock, "\n"))
				currentBlock = currentBlock[:0]
				inResponse = false
			}
			continue
		}

		// Skip JSON-like content (tool parameters)
		stripped := strings.TrimSpace(line)
		if stripped == "{" || stripped == "}" || stripped == "[" || stripped == "]" {
			continue
		}
		if strings.HasPrefix(stripped, "\"") && strings.HasSuffix(stripped, "\"") {
			continue
		}
		if strings.HasPrefix(stripped, "\"") && strings.Contains(stripped, "\":") {
			continue
		}

		// Lines starting with > are response content
		if strings.HasPrefix(line, "> ") {
			inResponse = true
			currentBlock = append(currentBlock, line[2:])
		} else if strings.HasPrefix(line, ">") {
			inResponse = true
			currentBlock = append(currentBlock, strings.TrimLeft(line[1:], " "))
		} else if inResponse && strings.TrimSpace(line) != "" {
			currentBlock = append(currentBlock, line)
		} else if strings.TrimSpace(line) == "" {
			if inResponse && len(currentBlock) > 0 {
				currentBlock = append(currentBlock, "")
			}
		}
	}

	if len(currentBlock) > 0 {
		responseBlocks = append(responseBlocks, strings.Join(currentBlock, "\n"))
	}

	// Return the longest block as the final answer
	if len(responseBlocks) > 0 {
		best := responseBlocks[0]
		for _, block := range responseBlocks[1:] {
			if len(block) > len(best) {
				best = block
			}
		}
		return strings.TrimSpace(best)
	}

	// Fallback: return all non-noise lines
	var filtered []string
	for _, line := range responseLines {
		if containsAny(line, skipPatterns) {
			continue
		}
		stripped := strings.TrimSpace(line)
		if stripped == "" || stripped == "{" || stripped == "}" || stripped == "[" || stripped == "]" {
			continue
		}
		if strings.HasPrefix(stripped, "\"") && (strings.Contains(stripped, "\":") || strings.HasSuffix(stripped, "\"")) {
			continue
		}
		filtered = append(filtered, line)
	}

	return strings.Join(filtered, "\n")
}

// containsAny checks if text contains any of the patterns.
func containsAny(text string, patterns []string) bool {
	for _, p := range patterns {
		if strings.Contains(text, p) {
			return true
		}
	}
	return false
}

// parseCommand splits a command string into executable and arguments,
// handling quoted paths (e.g., "C:\path with spaces\kiro-cli.exe" chat --flag).
func parseCommand(command string) []string {
	var parts []string
	var current strings.Builder
	inQuote := false

	for _, r := range command {
		switch {
		case r == '"':
			inQuote = !inQuote
		case r == ' ' && !inQuote:
			if current.Len() > 0 {
				parts = append(parts, current.String())
				current.Reset()
			}
		default:
			current.WriteRune(r)
		}
	}
	if current.Len() > 0 {
		parts = append(parts, current.String())
	}
	return parts
}
