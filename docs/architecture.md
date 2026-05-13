# 系統架構

## 資料流

```
用戶 (Telegram Forum Topic)
    │
    ▼
TelegramAdapter
    │ 根據 topic_id → 找到對應 instance
    │ /command → 本地處理（/help, /mode）
    │ 文字/檔案 → _process_and_reply()
    │
    ▼
Daemon.send_message()
    │ → ManagedProcess.send_input() (stdin)
    │ ← wait_response() 等待 ▸ Time: 標記
    │
    ▼
kiro-cli (獨立 process)
    │ 使用 MCP tools 回覆
    │ reply() → API → Telegram
    │
    ▼
Team MCP Server (stdio JSON-RPC)
    │ → HTTP → FastAPI (port 8470) → Telegram/Daemon
```

## 核心設計決策

| 決策 | 原因 |
|------|------|
| asyncio subprocess（非 tmux） | Windows 原生支援 |
| stdio JSON-RPC for MCP | 最小依賴，無 SDK |
| dataclass for config | 型別安全、可讀 |
| FastAPI for API | 自動文件、驗證 |
| Pydantic model 在模組層級 | 避免 `__future__ annotations` 相容問題 |
| 絕對路徑傳給 agent | agent CWD 與 daemon CWD 不同 |
| `--legacy-ui` 模式 | stdout 可解析，記憶體較低 |
| `os.execv` 完整重啟 | 確保程式碼更新生效 |

## 服務 Port

| 服務 | Port | 用途 |
|------|------|------|
| Team API | 8470 | 內部 REST API + MCP 通訊 |
| Telegram Bot | — | 透過 Bot API 輪詢 |

## 重啟機制

```
方式一：IDE Hook（fileEdited）
    → 停止 terminal → 清除 port → 重新啟動

方式二：leader-agent restart_team()
    → API /api/team/full-restart
    → stop_all() → os.execv() 重啟整個 daemon
    → 新 Python code 生效

方式三：restart_team()（soft）
    → API /api/team/restart
    → reload team.yaml → restart instances
    → Python code 不重載（僅 config 變更時用）
```

## 啟動流程

```
1. load .env
2. load team.yaml
3. start_all() → 每個 instance 啟動 kiro-cli
4. wait_for_ready() → 偵測 "All tools are now trusted"
5. start TelegramAdapter → polling
6. start API (FastAPI + uvicorn)
7. send_startup_greetings() → 每個 agent 回報狀態
```
