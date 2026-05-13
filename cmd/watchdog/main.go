package main

import (
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"time"
)

const (
	checkInterval = 30 * time.Second
	teamAgentPort = 8470
	maxRestarts   = 5
)

func isAlive(port int) bool {
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(fmt.Sprintf("http://127.0.0.1:%d/api/status", port))
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == 200
}

func startTeamAgent() *exec.Cmd {
	cmd := exec.Command("python", "-m", "kiro_multi_agent.cli", "team", "start")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err := cmd.Start()
	if err != nil {
		fmt.Printf("[watchdog] Failed to start: %v\n", err)
		return nil
	}
	fmt.Printf("[watchdog] Started team-agent (pid=%d)\n", cmd.Process.Pid)
	return cmd
}

func main() {
	fmt.Println("[watchdog] Starting...")
	cmd := startTeamAgent()
	time.Sleep(15 * time.Second)

	restartCount := 0
	lastReset := time.Now()

	for {
		if time.Since(lastReset) > time.Hour {
			restartCount = 0
			lastReset = time.Now()
		}

		alive := isAlive(teamAgentPort)
		procAlive := cmd != nil && cmd.ProcessState == nil

		if !alive || !procAlive {
			fmt.Printf("[watchdog] Service DOWN (api=%v, proc=%v)\n", alive, procAlive)
			if restartCount >= maxRestarts {
				fmt.Println("[watchdog] Max restarts reached")
			} else {
				if cmd != nil && cmd.Process != nil {
					cmd.Process.Kill()
					cmd.Wait()
				}
				time.Sleep(3 * time.Second)
				cmd = startTeamAgent()
				restartCount++
				time.Sleep(15 * time.Second)
			}
		}

		time.Sleep(checkInterval)
	}
}
