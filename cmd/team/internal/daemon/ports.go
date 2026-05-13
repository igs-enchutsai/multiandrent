// Port registry - tracks which ports are in use by which agents.
package daemon

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"path/filepath"
	"sync"
	"time"

	"kiro-multi-agent/internal/config"
)

// PortEntry represents a port allocation record.
type PortEntry struct {
	Port      int       `json:"port"`
	Instance  string    `json:"instance"`
	Purpose   string    `json:"purpose"`
	AllocAt   time.Time `json:"alloc_at"`
	Status    string    `json:"status"` // "active" | "released"
}

// PortRegistry manages port allocations for all agents.
type PortRegistry struct {
	mu      sync.Mutex
	entries map[int]*PortEntry
	path    string
}

// NewPortRegistry creates a port registry, loading existing state from disk.
func NewPortRegistry() *PortRegistry {
	home := config.GetHome()
	path := filepath.Join(home, "state", "ports.json")

	pr := &PortRegistry{
		entries: make(map[int]*PortEntry),
		path:    path,
	}
	pr.load()
	return pr
}

// Allocate checks if a port is available and registers it for an instance.
// Returns error if port is already in use.
func (pr *PortRegistry) Allocate(port int, instance string, purpose string) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	// Check if port is actually in use on the system
	if isPortInUse(port) {
		// Check if it's ours
		if entry, ok := pr.entries[port]; ok && entry.Instance == instance && entry.Status == "active" {
			// Same instance re-allocating, OK
			log.Printf("[ports] %s 重新使用 port %d (%s)", instance, port, purpose)
			return nil
		}
		// Someone else is using it
		existing := ""
		if entry, ok := pr.entries[port]; ok {
			existing = entry.Instance
		}
		return fmt.Errorf("port %d 已被佔用 (登記: %s)", port, existing)
	}

	// Check registry (might be stale)
	if entry, ok := pr.entries[port]; ok && entry.Status == "active" {
		// Port is registered but not actually in use - clean up stale entry
		if !isPortInUse(port) {
			log.Printf("[ports] 清理過期登記: port %d (原 %s)", port, entry.Instance)
			entry.Status = "released"
		} else if entry.Instance != instance {
			return fmt.Errorf("port %d 已被 %s 登記使用", port, entry.Instance)
		}
	}

	// Allocate
	pr.entries[port] = &PortEntry{
		Port:     port,
		Instance: instance,
		Purpose:  purpose,
		AllocAt:  time.Now(),
		Status:   "active",
	}

	log.Printf("[ports] 分配 port %d → %s (%s)", port, instance, purpose)
	pr.save()
	return nil
}

// Release marks a port as no longer in use.
func (pr *PortRegistry) Release(port int, instance string) {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	if entry, ok := pr.entries[port]; ok {
		if entry.Instance == instance {
			entry.Status = "released"
			log.Printf("[ports] 釋放 port %d ← %s", port, instance)
			pr.save()
		}
	}
}

// ReleaseAll releases all ports for a given instance.
func (pr *PortRegistry) ReleaseAll(instance string) {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	for _, entry := range pr.entries {
		if entry.Instance == instance && entry.Status == "active" {
			entry.Status = "released"
			log.Printf("[ports] 釋放 port %d ← %s", entry.Port, instance)
		}
	}
	pr.save()
}

// GetAll returns all current port allocations.
func (pr *PortRegistry) GetAll() []PortEntry {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	var result []PortEntry
	for _, entry := range pr.entries {
		if entry.Status == "active" {
			result = append(result, *entry)
		}
	}
	return result
}

// CleanStale removes entries for ports that are no longer actually in use.
func (pr *PortRegistry) CleanStale() int {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	cleaned := 0
	for port, entry := range pr.entries {
		if entry.Status == "active" && !isPortInUse(port) {
			entry.Status = "released"
			cleaned++
			log.Printf("[ports] 清理過期: port %d (%s)", port, entry.Instance)
		}
	}
	if cleaned > 0 {
		pr.save()
	}
	return cleaned
}

func (pr *PortRegistry) load() {
	data, err := os.ReadFile(pr.path)
	if err != nil {
		return // File doesn't exist yet, start fresh
	}

	var entries []PortEntry
	if err := json.Unmarshal(data, &entries); err != nil {
		return
	}

	for i := range entries {
		if entries[i].Status == "active" {
			pr.entries[entries[i].Port] = &entries[i]
		}
	}
}

func (pr *PortRegistry) save() {
	var entries []PortEntry
	for _, entry := range pr.entries {
		entries = append(entries, *entry)
	}

	data, err := json.MarshalIndent(entries, "", "  ")
	if err != nil {
		return
	}

	dir := filepath.Dir(pr.path)
	os.MkdirAll(dir, 0755)
	os.WriteFile(pr.path, data, 0644)
}

// isPortInUse checks if a TCP port is currently bound on localhost.
func isPortInUse(port int) bool {
	ln, err := net.Listen("tcp", fmt.Sprintf("127.0.0.1:%d", port))
	if err != nil {
		return true // Port is in use
	}
	ln.Close()
	return false
}
