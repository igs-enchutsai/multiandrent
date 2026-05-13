// Kiro Multi-Agent Team Manager - Go implementation.
// CLI entry point with subcommands: team start, team stop, team status, init, mcp.
package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"syscall"

	"kiro-multi-agent/internal/api"
	"kiro-multi-agent/internal/config"
	"kiro-multi-agent/internal/daemon"
	"kiro-multi-agent/internal/mcp"
	"kiro-multi-agent/internal/telegram"

	"github.com/joho/godotenv"
)

func main() {
	log.SetFlags(log.Ltime | log.Lmsgprefix)
	log.SetPrefix("")

	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	switch os.Args[1] {
	case "team":
		if len(os.Args) < 3 {
			fmt.Println("用法: team <start|stop|status>")
			os.Exit(1)
		}
		switch os.Args[2] {
		case "start":
			cmdTeamStart()
		case "stop":
			cmdTeamStop()
		case "status":
			cmdTeamStatus()
		default:
			fmt.Printf("未知的 team 子命令: %s\n", os.Args[2])
			os.Exit(1)
		}
	case "init":
		cmdInit()
	case "mcp":
		if len(os.Args) < 3 {
			fmt.Println("用法: mcp <team|hoyeah>")
			os.Exit(1)
		}
		switch os.Args[2] {
		case "team":
			cmdMCPTeam()
		case "hoyeah":
			cmdMCPHoYeah()
		default:
			fmt.Printf("未知的 mcp 子命令: %s\n", os.Args[2])
			os.Exit(1)
		}
	default:
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println(`Kiro Multi-Agent Team Manager

用法:
  team start     啟動所有 agent 實例
  team stop      停止所有 agent 實例
  team status    顯示實例狀態
  init           建立預設 team.yaml
  mcp team       啟動 Team MCP Server (stdio)
  mcp hoyeah     啟動 HoYeah MCP Server (stdio)`)
}

func cmdTeamStart() {
	// Load .env
	home := config.GetHome()
	godotenv.Load(filepath.Join(home, ".env"))
	godotenv.Load(".env")

	cfg, err := config.LoadTeamConfig("")
	if err != nil {
		log.Fatalf("載入設定失敗: %v", err)
	}

	log.Printf("啟動 team (%d 個實例)...", len(cfg.Instances))

	// Create daemon
	d := daemon.New(cfg)
	results := d.StartAll()

	running := 0
	for _, ok := range results {
		if ok {
			running++
		}
	}
	log.Printf("Team 就緒: %d/%d 運行中", running, len(results))

	// Start Telegram adapter
	var tg *telegram.Adapter
	tg = telegram.New(cfg, d)
	if err := tg.Start(); err != nil {
		log.Printf("Telegram 啟動失敗: %v (繼續運行)", err)
		tg = nil
	}

	// Start API server - check port availability first
	if err := d.Ports.Allocate(cfg.HealthPort, "team-api", "REST API"); err != nil {
		log.Fatalf("API port 分配失敗: %v", err)
	}
	apiServer := api.New(d, tg)
	if err := apiServer.Start(cfg.HealthPort); err != nil {
		d.Ports.Release(cfg.HealthPort, "team-api")
		log.Fatalf("API 啟動失敗: %v", err)
	}

	// Write PID file
	pidFile := filepath.Join(home, "team.pid")
	os.WriteFile(pidFile, []byte(strconv.Itoa(os.Getpid())), 0644)

	// Wait for shutdown signal
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	<-sigCh

	log.Println("收到停止信號，正在關閉...")

	// Cleanup
	if tg != nil {
		tg.Stop()
	}
	apiServer.Stop()
	d.Ports.Release(cfg.HealthPort, "team-api")
	d.StopAll()
	os.Remove(pidFile)

	log.Println("已關閉")
}

func cmdTeamStop() {
	home := config.GetHome()
	pidFile := filepath.Join(home, "team.pid")

	data, err := os.ReadFile(pidFile)
	if err != nil {
		fmt.Println("找不到 team.pid，可能未運行")
		return
	}

	pid, err := strconv.Atoi(string(data))
	if err != nil {
		fmt.Println("team.pid 格式錯誤")
		return
	}

	proc, err := os.FindProcess(pid)
	if err != nil {
		fmt.Printf("找不到程序 (pid=%d)\n", pid)
		return
	}

	if err := proc.Signal(syscall.SIGTERM); err != nil {
		fmt.Printf("發送停止信號失敗: %v\n", err)
		return
	}

	fmt.Println("已發送停止信號")
}

func cmdTeamStatus() {
	home := config.GetHome()
	godotenv.Load(filepath.Join(home, ".env"))

	cfg, err := config.LoadTeamConfig("")
	if err != nil {
		log.Fatalf("載入設定失敗: %v", err)
	}

	fmt.Printf("Team 設定: %d 個實例\n", len(cfg.Instances))
	for name, ic := range cfg.Instances {
		model := ic.Model
		if model == "" {
			model = "auto"
		}
		fmt.Printf("  %-20s backend=%-10s model=%s\n", name, ic.Backend, model)
	}
}

func cmdInit() {
	home := config.GetHome()
	teamYaml := filepath.Join(home, "team.yaml")

	if _, err := os.Stat(teamYaml); err == nil {
		fmt.Printf("設定已存在: %s\n", teamYaml)
		return
	}

	content := `# kiro-multi-agent team config
channel:
  bot_token_env: TELEGRAM_BOT_TOKEN
  group_id: 0
  general_topic_id: 1

access:
  mode: locked
  allowed_users: []

defaults:
  backend: kiro-cli
  model: claude-sonnet-4

instances: {}

health_port: 8470
`
	if err := os.WriteFile(teamYaml, []byte(content), 0644); err != nil {
		log.Fatalf("建立 team.yaml 失敗: %v", err)
	}
	fmt.Printf("已建立: %s\n", teamYaml)
	fmt.Println("編輯 team.yaml，然後執行: team start")
}

func cmdMCPTeam() {
	// Load .env from multiple locations
	godotenv.Load(".env")
	godotenv.Load("../../.env")
	godotenv.Load("../../../.env")

	port := 8470
	instance := "unknown"
	role := "worker"

	// Parse flags from os.Args[3:]
	args := os.Args[3:]
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--port":
			if i+1 < len(args) {
				port, _ = strconv.Atoi(args[i+1])
				i++
			}
		case "--instance":
			if i+1 < len(args) {
				instance = args[i+1]
				i++
			}
		case "--role":
			if i+1 < len(args) {
				role = args[i+1]
				i++
			}
		}
	}

	server := &mcp.TeamServer{
		Port:     port,
		Instance: instance,
		Role:     role,
	}
	server.Run()
}

func cmdMCPHoYeah() {
	// Load .env from multiple locations
	godotenv.Load(".env")
	godotenv.Load("../../.env")
	godotenv.Load("../../../.env")

	server := &mcp.HoYeahServer{}
	server.Run()
}
