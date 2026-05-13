# Kiro Multi-Agent Framework

A multi AI Agent team management framework built on Kiro CLI.
Coordinate multiple Kiro CLI instances via Telegram Bot with cross-agent communication.

## Architecture

```
watchdog (Go/Python)           <- Process management, health check, auto-restart
+-- team-agent (Python)        <- Telegram Bot + Kiro CLI management
|   +-- TelegramAdapter        <- Message routing (Forum Topic -> Agent)
|   +-- Daemon                 <- Instance lifecycle management
|   +-- DaemonAPI (FastAPI)    <- REST API + WebSocket
|   +-- MCP Server             <- Cross-agent communication (stdio JSON-RPC)
+-- Agent Instances            <- Independent Kiro CLI processes
    +-- agent-a/
    +-- agent-b/
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Initialize
kiro-multi-agent init

# Configure team.yaml with your Telegram Bot Token and agents

# Start
kiro-multi-agent team start

# Or with watchdog (recommended for production)
python scripts/watchdog.py
```

## Key Concepts

### Steering (Behavior Rules)
Each agent has `.kiro/steering/` files that control AI behavior, reply style, and work patterns.

### MCP Server (Cross-Agent Communication)
Each agent gets a stdio JSON-RPC MCP server injected at startup, providing tools like
`reply()`, `query_team_status()`, `log_to_leader()`, `send_to_instance()`.

### Watchdog (Process Monitor)
External monitor that checks service health every 30s and auto-restarts crashed services.
Available in both Python (development) and Go (production) versions.

### Hook (Event-Driven Automation)
Kiro IDE hooks trigger actions on file changes, tool calls, etc.

## Technology Stack

| Tech | Purpose |
|------|---------|
| Python >= 3.11 | Main framework |
| Go 1.24+ | Watchdog, HTTP servers |
| FastAPI | REST API |
| python-telegram-bot | Telegram Bot API |
| asyncio | Async I/O |
| SQLite | Event log, session, cost tracking |

## Creating a New Agent

```bash
# 1. Copy template
cp -r templates/agent-template agents/my-new-agent

# 2. Edit MCP config (replace __AGENT_NAME__)
# 3. Add steering files for your domain
# 4. Add to team.yaml
# 5. Create Telegram Forum Topic
# 6. Restart team
```

## License

MIT
