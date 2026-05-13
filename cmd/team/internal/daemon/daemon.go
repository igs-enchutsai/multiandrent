// Package daemon manages multiple kiro-cli instances with health monitoring.
package daemon

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"sync"
	"time"

	"kiro-multi-agent/internal/config"
	"kiro-multi-agent/internal/process"
)

// InstanceStatus represents the state of an instance.
type InstanceStatus string

const (
	StatusStopped  InstanceStatus = "stopped"
	StatusStarting InstanceStatus = "starting"
	StatusRunning  InstanceStatus = "running"
	StatusCrashed  InstanceStatus = "crashed"
)

var readyPattern = regexp.MustCompile(`All tools are now trusted|Trust All Tools active|ask a question`)

// InstanceState holds runtime state for a single instance.
type InstanceState struct {
	Config       *config.InstanceConfig
	Status       InstanceStatus
	Process      *process.ManagedProcess
	CrashCount   int
	LastActivity time.Time
	stopHealth   chan struct{}
}

// StatusInfo is returned by GetStatus for API consumers.
type StatusInfo struct {
	Name   string `json:"name"`
	Status string `json:"status"`
	PID    int    `json:"pid"`
}

// Daemon manages the lifecycle of all Kiro CLI instances.
type Daemon struct {
	Config    *config.TeamConfig
	Ports     *PortRegistry
	instances map[string]*InstanceState
	mu        sync.RWMutex
}

// New creates a new Daemon.
func New(cfg *config.TeamConfig) *Daemon {
	ports := NewPortRegistry()
	// Clean stale entries on startup
	if cleaned := ports.CleanStale(); cleaned > 0 {
		log.Printf("[daemon] 清理了 %d 個過期 port 登記", cleaned)
	}
	return &Daemon{
		Config:    cfg,
		Ports:     ports,
		instances: make(map[string]*InstanceState),
	}
}

// StartInstance starts a single kiro-cli instance.
func (d *Daemon) StartInstance(name string) error {
	ic, ok := d.Config.Instances[name]
	if !ok {
		return fmt.Errorf("未知的 instance: %s", name)
	}

	d.mu.Lock()
	state, exists := d.instances[name]
	if exists && state.Status == StatusRunning {
		d.mu.Unlock()
		return nil
	}
	if !exists {
		state = &InstanceState{Config: ic}
		d.instances[name] = state
	}
	state.Status = StatusStarting
	d.mu.Unlock()

	// Write MCP config
	d.writeMCPConfig(ic, name)

	// Build command
	binaryPath := findKiroCLI()
	cmd := fmt.Sprintf(`"%s" chat --trust-all-tools --legacy-ui`, binaryPath)
	if ic.Model != "" {
		cmd += " --model " + ic.Model
	}

	cwd, _ := filepath.Abs(ic.WorkingDirectory)
	os.MkdirAll(cwd, 0755)

	mp := &process.ManagedProcess{Name: name}
	if err := mp.Start(cmd, cwd); err != nil {
		d.mu.Lock()
		state.Status = StatusCrashed
		d.mu.Unlock()
		return fmt.Errorf("啟動 %s 失敗: %w", name, err)
	}

	d.mu.Lock()
	state.Process = mp
	d.mu.Unlock()

	// Wait for ready
	ready := d.waitForReady(state, 90*time.Second)
	if ready {
		d.mu.Lock()
		state.Status = StatusRunning
		state.LastActivity = time.Now()
		state.stopHealth = make(chan struct{})
		d.mu.Unlock()
		log.Printf("[daemon] %s 已就緒 (pid=%d)", name, mp.PID())
		go d.healthLoop(name)
	} else {
		d.mu.Lock()
		state.Status = StatusCrashed
		d.mu.Unlock()
		output := mp.Capture(10)
		log.Printf("[daemon] %s 啟動失敗。最後輸出: %s", name, lastN(output, 300))
	}

	return nil
}

// StopInstance stops a single instance.
func (d *Daemon) StopInstance(name string) {
	d.mu.Lock()
	state, ok := d.instances[name]
	if !ok || state.Status == StatusStopped {
		d.mu.Unlock()
		return
	}
	if state.stopHealth != nil {
		close(state.stopHealth)
		state.stopHealth = nil
	}
	d.mu.Unlock()

	if state.Process != nil {
		state.Process.Kill()
	}

	d.mu.Lock()
	state.Status = StatusStopped
	d.mu.Unlock()
	log.Printf("[daemon] %s 已停止", name)
}

// SendMessage sends text to an instance and waits for the response.
func (d *Daemon) SendMessage(name string, text string) (string, error) {
	d.mu.RLock()
	state, ok := d.instances[name]
	d.mu.RUnlock()

	if !ok || state.Status != StatusRunning || state.Process == nil {
		return "", fmt.Errorf("instance %s 未運行", name)
	}

	if err := state.Process.SendInput(text); err != nil {
		return "", fmt.Errorf("發送訊息失敗: %w", err)
	}

	d.mu.Lock()
	state.LastActivity = time.Now()
	d.mu.Unlock()

	response := state.Process.WaitResponse()
	return response, nil
}

// StartAll starts all configured instances.
func (d *Daemon) StartAll() map[string]bool {
	results := make(map[string]bool)
	var mu sync.Mutex
	var wg sync.WaitGroup

	for name := range d.Config.Instances {
		wg.Add(1)
		go func(n string) {
			defer wg.Done()
			err := d.StartInstance(n)
			mu.Lock()
			results[n] = err == nil && d.getStatus(n) == StatusRunning
			mu.Unlock()
		}(name)
	}
	wg.Wait()
	return results
}

// StopAll stops all running instances.
func (d *Daemon) StopAll() {
	d.mu.RLock()
	names := make([]string, 0, len(d.instances))
	for name := range d.instances {
		names = append(names, name)
	}
	d.mu.RUnlock()

	var wg sync.WaitGroup
	for _, name := range names {
		wg.Add(1)
		go func(n string) {
			defer wg.Done()
			d.StopInstance(n)
		}(name)
	}
	wg.Wait()
}

// GetStatus returns status info for all instances.
func (d *Daemon) GetStatus() []StatusInfo {
	d.mu.RLock()
	defer d.mu.RUnlock()

	var result []StatusInfo
	for name, state := range d.instances {
		pid := 0
		if state.Process != nil {
			pid = state.Process.PID()
		}
		result = append(result, StatusInfo{
			Name:   name,
			Status: string(state.Status),
			PID:    pid,
		})
	}
	return result
}

func (d *Daemon) getStatus(name string) InstanceStatus {
	d.mu.RLock()
	defer d.mu.RUnlock()
	if state, ok := d.instances[name]; ok {
		return state.Status
	}
	return StatusStopped
}

func (d *Daemon) waitForReady(state *InstanceState, timeout time.Duration) bool {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		if state.Process == nil || !state.Process.IsAlive() {
			log.Printf("[daemon] %s 程序在啟動期間終止", state.Config.Name)
			return false
		}
		output := state.Process.Capture(50)
		if readyPattern.MatchString(output) {
			return true
		}
		time.Sleep(2 * time.Second)
	}
	log.Printf("[daemon] %s 等待就緒超時", state.Config.Name)
	return false
}

func (d *Daemon) healthLoop(name string) {
	d.mu.RLock()
	state := d.instances[name]
	interval := time.Duration(state.Config.RestartPolicy.HealthCheckIntervalMs) * time.Millisecond
	stopCh := state.stopHealth
	d.mu.RUnlock()

	for {
		select {
		case <-stopCh:
			return
		case <-time.After(interval):
		}

		d.mu.RLock()
		st := d.instances[name]
		d.mu.RUnlock()

		if st == nil || st.Status != StatusRunning {
			return
		}

		if st.Process == nil || !st.Process.IsAlive() {
			d.mu.Lock()
			st.Status = StatusCrashed
			st.CrashCount++
			d.mu.Unlock()
			log.Printf("[daemon] %s 崩潰 (次數=%d)", name, st.CrashCount)

			if st.CrashCount <= st.Config.RestartPolicy.MaxRetries {
				delay := time.Duration(math.Min(math.Pow(2, float64(st.CrashCount)), 60)) * time.Second
				time.Sleep(delay)
				d.StartInstance(name)
			}
			return
		}
	}
}

func (d *Daemon) writeMCPConfig(ic *config.InstanceConfig, name string) {
	mcpDir := filepath.Join(ic.WorkingDirectory, ".kiro", "settings")
	os.MkdirAll(mcpDir, 0755)
	mcpPath := filepath.Join(mcpDir, "mcp.json")

	// Load existing config
	existing := map[string]interface{}{}
	if data, err := os.ReadFile(mcpPath); err == nil {
		json.Unmarshal(data, &existing)
	}

	servers, ok := existing["mcpServers"].(map[string]interface{})
	if !ok {
		servers = map[string]interface{}{}
	}

	// Find project root for `go run` mode MCP server
	projectRoot := findProjectRoot()
	goPath := findGoBinary()
	servers["team"] = map[string]interface{}{
		"command": goPath,
		"args": []string{
			"run", filepath.Join(projectRoot, "cmd", "team"),
			"mcp", "team",
			"--port", fmt.Sprintf("%d", d.Config.HealthPort),
			"--instance", name,
			"--role", ic.Role,
		},
	}

	existing["mcpServers"] = servers
	data, _ := json.MarshalIndent(existing, "", "  ")
	os.WriteFile(mcpPath, data, 0644)
}

func findProjectRoot() string {
	// Look for team.yaml to find project root
	dir, _ := os.Getwd()
	for {
		if _, err := os.Stat(filepath.Join(dir, "team.yaml")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	// Fallback to CWD
	cwd, _ := os.Getwd()
	return cwd
}

func findGoBinary() string {
	if path, err := findInPath("go"); err == nil {
		return path
	}
	if runtime.GOOS == "windows" {
		// Common Go install locations on Windows
		candidates := []string{
			`C:\Program Files\Go\bin\go.exe`,
			`C:\Go\bin\go.exe`,
		}
		for _, c := range candidates {
			if _, err := os.Stat(c); err == nil {
				return c
			}
		}
	}
	return "go"
}

func findKiroCLI() string {
	if runtime.GOOS == "windows" {
		localAppData := os.Getenv("LOCALAPPDATA")
		candidates := []string{
			filepath.Join(localAppData, "Programs", "Kiro-Cli", "LocalApp", "Kiro-Cli", "kiro-cli.exe"),
			filepath.Join(localAppData, "Programs", "Kiro-Cli", "kiro-cli.exe"),
		}
		for _, c := range candidates {
			if _, err := os.Stat(c); err == nil {
				return c
			}
		}
	}
	// Try PATH
	if path, err := findInPath("kiro-cli"); err == nil {
		return path
	}
	return "kiro-cli"
}

func findInPath(name string) (string, error) {
	pathEnv := os.Getenv("PATH")
	var sep string
	if runtime.GOOS == "windows" {
		sep = ";"
	} else {
		sep = ":"
	}
	for _, dir := range strings.Split(pathEnv, sep) {
		full := filepath.Join(dir, name)
		if runtime.GOOS == "windows" {
			full += ".exe"
		}
		if _, err := os.Stat(full); err == nil {
			return full, nil
		}
	}
	return "", fmt.Errorf("not found: %s", name)
}

func lastN(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[len(s)-n:]
}
