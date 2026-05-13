---
inclusion: always
---

# Technology Stack

## 語言分工（強制）

| 用途 | 語言 | 說明 |
|------|------|------|
| 工具開發、爬蟲、HTTP server、CLI | **Go** | 所有新功能預設用 Go |
| Multi-Agent 框架 | Python | daemon、telegram adapter、MCP server |
| Agent 任務產出 | **Go** | 除非用戶明確要求 Python |

## Python（僅限 Multi-Agent 框架）
- Python >= 3.11
- `from __future__ import annotations`
- Type annotations: 3.11+ syntax (str | None, list[str])
- src layout: source in src/kiro_multi_agent/
- CLI entry: kiro-multi-agent -> kiro_multi_agent.cli:main

## Go（工具與 Agent 開發）
- Go 1.22+
- 專案放在 `cmd/{project-name}/`
- 用 `go run .` 執行，不產生 exe
- 環境變數用 `os.Getenv()`

## Key Design Choices
- asyncio subprocess for process management (Windows-native)
- Hand-written stdio JSON-RPC for MCP Server (no SDK dependency)
- dataclass for all config and state structures
- Pydantic BaseModel 定義在模組層級（不可在函數內）
- kiro-cli 強制 `--legacy-ui` 模式
- 預設模型：claude-opus-4.6
