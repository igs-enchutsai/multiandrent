# Kiro Multi-Agent Framework 教學指南

> 用 Kiro CLI + Telegram Bot 建立多 AI Agent 協作團隊的完整教學。
> 每個 Agent 是獨立的 Kiro CLI instance，透過 Telegram Forum Topic 接收指令，
> 透過 MCP Server 進行跨 Agent 通訊。

---

## 目錄

1. [這是什麼](#一這是什麼)
2. [系統架構](#二系統架構)
3. [環境準備](#三環境準備)
4. [安裝與設定](#四安裝與設定)
5. [核心概念](#五核心概念)
6. [建立你的第一個 Agent](#六建立你的第一個-agent)
7. [啟動與運行](#七啟動與運行)
8. [開發自訂 MCP Server](#八開發自訂-mcp-server)
9. [Steering 行為控制](#九-steering-行為控制)
10. [進階：Watchdog 與自動重啟](#十進階watchdog-與自動重啟)
11. [故障排除](#十一故障排除)
12. [專案結構總覽](#十二專案結構總覽)

---

## 一、這是什麼

Kiro Multi-Agent 是一個框架，讓你可以：

- 同時運行多個 AI Agent（每個都是獨立的 Kiro CLI）
- 透過 Telegram Bot 與每個 Agent 對話（每個 Agent 有自己的 Forum Topic）
- Agent 之間可以互相通訊（透過 MCP Server）
- 自動健康檢查與崩潰重啟
- 統一管理環境變數、Port、行為規則

### 適用場景

| 場景 | 範例 |
|------|------|
| 團隊協作 | Leader 分派任務給 Worker Agent |
| 專業分工 | 一個 Agent 查數據、一個 Agent 寫程式、一個 Agent 爬資料 |
| 長時間任務 | Agent 持續運行，隨時接收 Telegram 指令 |
| 多專案管理 | 每個 Agent 負責不同專案目錄 |

---

## 二、系統架構

```
┌─────────────────────────────────────────────────────┐
│                    Telegram Group                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Leader   │  │ Worker-A │  │ Worker-B │  ...     │
│  │ Topic    │  │ Topic    │  │ Topic    │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼──────────────┼──────────────┼───────────────┘
        │              │              │
┌───────▼──────────────▼──────────────▼───────────────┐
│              Team Manager (Go / Python)               │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ TelegramAdapter（訊息路由 by topic_id）      │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │ Daemon（kiro-cli subprocess 生命週期管理）    │    │
│  │  ├── leader-agent  (kiro-cli instance)      │    │
│  │  ├── worker-a      (kiro-cli instance)      │    │
│  │  └── worker-b      (kiro-cli instance)      │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │ REST API (port 8470) ← 跨 Agent 通訊        │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### 訊息流程

1. 用戶在 Telegram Forum Topic 發訊息
2. TelegramAdapter 根據 `topic_id` 路由到對應 Agent
3. 訊息寫入 kiro-cli 的 stdin
4. kiro-cli 處理後輸出到 stdout
5. 系統偵測 `▸ Time:` 標記 → 回覆完成
6. 過濾 ANSI/spinner 噪音，提取最終回覆
7. 回覆發送到 Telegram 對應 Topic

---

## 三、環境準備

### 必要軟體

| 軟體 | 版本 | 用途 | 安裝方式 |
|------|------|------|---------|
| Go | 1.22+ | Team Manager 主程式 | https://go.dev/dl/ |
| Python | 3.11+ | MCP Server、輔助工具 | https://python.org |
| Kiro CLI | 2.2+ | Agent 大腦（AI 推理引擎） | Kiro IDE 內建 |
| Git | 任意 | 版本控制 | https://git-scm.com |

### 確認安裝

```bash
go version          # go1.22.0 or higher
python --version    # Python 3.11+
kiro-cli whoami     # 確認已登入
git --version
```

### Telegram 準備

1. 建立一個 Telegram Bot（透過 @BotFather）
2. 建立一個 Telegram Group，開啟 Forum Topics 功能
3. 把 Bot 加入 Group 並設為管理員（需要「管理話題」權限）
4. 記下 Bot Token、Group ID

---

## 四、安裝與設定

### 1. Clone 專案

```bash
git clone <your-repo-url>
cd KiroMultiAgent
```

### 2. 安裝 Python 依賴

```bash
pip install -e ".[dev]"
```

### 3. 設定環境變數

```bash
cp .env.example .env
```

編輯 `.env`：

```env
# Telegram Bot Token（從 @BotFather 取得）
TELEGRAM_BOT_TOKEN=your_bot_token_here

# HoYeah API（如果有營運數據查詢需求）
HOYEAH_API_BASE=http://your-api-server:8642/v1/
HOYEAH_API_KEY=your_api_key_here
```

> **重要**：`.env` 已在 `.gitignore` 中，不會被 commit。所有 secret 只放這裡。

### 4. 設定 team.yaml

```bash
cp examples/team.yaml team.yaml
```

編輯 `team.yaml`：

```yaml
channel:
  bot_token_env: TELEGRAM_BOT_TOKEN    # 對應 .env 中的變數名
  group_id: -100xxxxxxxxxx             # 你的 Telegram Group ID
  general_topic_id: 1

access:
  mode: locked
  allowed_users: [123456789]           # 你的 Telegram User ID

defaults:
  backend: kiro-cli
  model: claude-sonnet-4               # 預設模型

cost_guard:
  daily_limit_usd: 10.0
  warn_at_percentage: 80

instances:
  leader-agent:
    working_directory: ./agents/leader-agent
    description: "Team leader - task coordination"
    topic_id: 1                        # Telegram Forum Topic ID
    role: leader
    general_topic: true

health_port: 8470
```

### 5. 取得 Telegram ID

如果不知道 Group ID 或 Topic ID，用這個工具：

```bash
python scripts/get_ids.py
```

然後在 Telegram Group 的各個 Topic 發訊息，終端會印出對應的 ID。

---

## 五、核心概念

### Agent

一個 Agent = 一個獨立的 kiro-cli instance，擁有：

| 組成 | 說明 |
|------|------|
| Working Directory | `agents/{name}/`，Agent 的工作空間 |
| Steering | `.kiro/steering/*.md`，控制 AI 行為的規則 |
| MCP Server | `.kiro/settings/mcp.json`，提供工具能力 |
| Telegram Topic | 對話入口，用戶在這裡與 Agent 互動 |

### Steering（行為規則）

Markdown 檔案，kiro-cli 啟動時自動載入作為系統指令。用來控制：
- AI 的角色定義
- 回覆風格
- 技術選型
- 錯誤處理策略

### MCP Server（工具能力）

Model Context Protocol Server，透過 stdio JSON-RPC 提供 Agent 可呼叫的工具：

| 工具 | 用途 |
|------|------|
| `reply(text)` | 回覆用戶（透過 Telegram） |
| `query_team_status()` | 查詢團隊狀態 |
| `log_to_leader(text)` | 向 Leader 回報（用戶看不到） |
| `report_progress(message)` | 回報任務進度 |
| `send_to_instance(instance, message)` | 發訊息給其他 Agent（僅 Leader） |

### Team Manager

負責所有 Agent 的生命週期管理：
- 啟動/停止 kiro-cli instance
- Telegram 訊息路由
- REST API（跨 Agent 通訊）
- 健康檢查與自動重啟

---

## 六、建立你的第一個 Agent

### 步驟一：從 Template 複製

```bash
cp -r templates/agent-template agents/my-first-agent
```

複製後的結構：

```
agents/my-first-agent/
├── .kiro/
│   ├── settings/
│   │   └── mcp.json          ← 需修改
│   └── steering/
│       ├── 00-agent-rules.md  ← 核心行為規則
│       ├── error-recovery.md  ← 錯誤處理 SOP
│       └── tech-stack.md      ← 技術選型指南
├── logs/
│   └── .gitkeep
└── README.md
```

### 步驟二：修改 MCP 設定

編輯 `agents/my-first-agent/.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "team": {
      "command": "go",
      "args": [
        "run", "./cmd/team",
        "mcp", "team",
        "--port", "8470",
        "--instance", "my-first-agent",
        "--role", "worker"
      ]
    }
  }
}
```

把 `__AGENT_NAME__` 替換為你的 agent 名稱。

> 注意：啟動時 Daemon 會自動覆寫這個檔案，所以手動修改主要是為了獨立測試。

### 步驟三：加入語言設定

建立 `agents/my-first-agent/.kiro/steering/language.md`：

```markdown
---
inclusion: always
---

# 語言規則

- 一律使用繁體中文回覆
- 技術術語可保留英文
```

### 步驟四：加入專屬 Steering

根據 Agent 用途建立專屬規則。例如一個「程式開發」Agent：

建立 `agents/my-first-agent/.kiro/steering/project.md`：

```markdown
---
inclusion: always
---

# 開發 Agent 規格

## 角色
你是一位全端工程師，負責實作指定的功能需求。

## 工作流程
1. 收到需求後，先確認理解正確
2. 列出實作計畫
3. 逐步實作，每完成一個步驟回報進度
4. 完成後提供測試方式

## 技術棧
- 語言：Go 1.22+ / Python 3.11+
- 不產生 exe 檔案，用 `go run .` 執行
```

### 步驟五：建立 Telegram Forum Topic

在你的 Telegram Group 中建立一個新的 Forum Topic（例如叫「My First Agent」），記下 topic_id。

或用程式建立：

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
r = requests.post(
    f"https://api.telegram.org/bot{token}/createForumTopic",
    json={"chat_id": -100xxxxxxxxxx, "name": "My First Agent"}
)
print(r.json())  # 記下 message_thread_id
```

### 步驟六：更新 team.yaml

```yaml
instances:
  # ... 其他 agent ...

  my-first-agent:
    working_directory: ./agents/my-first-agent
    description: "我的第一個 Agent"
    topic_id: 42        # 從步驟五取得
    role: worker
```

### 步驟七：啟動並驗證

```bash
cd cmd/team && go run . team start
```

在 Telegram 對應 Topic 發訊息，確認 Agent 有回覆。

---

## 七、啟動與運行

### 啟動 Team

```bash
# Go 版本（推薦）
cd cmd/team && go run . team start

# Python 版本（開發用）
kiro-multi-agent team start
# 或
python -m kiro_multi_agent team start
```

### 停止 Team

- 終端按 `Ctrl+C`
- 或執行 `cd cmd/team && go run . team stop`

### 查看狀態

```bash
# CLI
cd cmd/team && go run . team status

# API
curl http://127.0.0.1:8470/api/status
```

### 使用啟動腳本（支援自動重啟）

Windows：
```bat
scripts\start-team.bat
```

Linux/Mac：
```bash
bash scripts/start-team.sh
```

這些腳本會在程式退出時檢查 `restart.flag` 檔案，如果存在就自動重啟。

---

## 八、開發自訂 MCP Server

MCP Server 讓 Agent 擁有「工具能力」。以下是建立自訂 MCP Server 的範例。

### 架構：stdio JSON-RPC

```
kiro-cli  ──stdin──>  MCP Server (your code)
kiro-cli  <──stdout──  MCP Server (your code)
```

通訊協定是 JSON-RPC 2.0，每行一個 JSON 物件。

### 範例：建立一個查詢 API 的 MCP Server

```python
"""my_api_mcp.py - 自訂 MCP Server 範例"""
from __future__ import annotations

import json
import os
import sys

def query_my_api(question: str) -> str:
    """你的 API 查詢邏輯"""
    api_key = os.getenv("MY_API_KEY", "")
    if not api_key:
        return "錯誤：未設定 MY_API_KEY"
    # ... 實作查詢邏輯 ...
    return "查詢結果"

# 工具定義
TOOLS = [
    {
        "name": "query_my_api",
        "description": "查詢我的 API",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "查詢問題"}
            },
            "required": ["question"],
        },
    }
]

def handle_request(req: dict) -> dict | None:
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "my-api", "version": "1.0.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        if tool_name == "query_my_api":
            result = query_my_api(arguments.get("question", ""))
        else:
            result = f"未知工具: {tool_name}"
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"content": [{"type": "text", "text": result}]},
        }
    return {
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": -32601, "message": f"Unknown: {method}"},
    }

def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_request(req)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
```

### 註冊到 Agent

在 `agents/{name}/.kiro/settings/mcp.json` 加入：

```json
{
  "mcpServers": {
    "team": { "..." },
    "my-api": {
      "command": "python",
      "args": ["-m", "my_api_mcp"],
      "env": {
        "MY_API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

---

## 九、Steering 行為控制

### 層級結構

```
.kiro/steering/                    ← Workspace 級（開發者看得到）
  ├── coding-rules.md
  ├── structure.md
  └── tech.md

agents/{name}/.kiro/steering/      ← Agent 級（只有該 Agent 看得到）
  ├── 00-agent-rules.md            ← 核心規則（from template）
  ├── error-recovery.md            ← 錯誤處理（from template）
  ├── tech-stack.md                ← 技術指南（from template）
  ├── language.md                  ← 回覆語言
  └── project.md                   ← 專屬規格書
```

### Steering 檔案格式

```markdown
---
inclusion: always
---

# 標題

你的規則內容...
```

`inclusion: always` = 每次對話都載入。

### Template 提供的基礎 Steering

| 檔案 | 內容 | 可否刪除 |
|------|------|---------|
| `00-agent-rules.md` | 進度回報、程式原則、錯誤處理、回覆風格 | 可覆蓋 |
| `error-recovery.md` | L1/L2/L3 錯誤分級、重試策略 | **不可刪除** |
| `tech-stack.md` | Go/Python 選型、Port 規則、防毒規則 | **不可刪除** |

### 常見 Steering 範例

**對話型 Agent（客服、查詢）：**
```markdown
---
inclusion: always
---

# 營運數據查詢助手

## 角色
你是營運數據查詢助手，使用 query_hoyeah 工具回答數據問題。

## 回覆策略
1. 收到問題 → 呼叫 query_hoyeah
2. 收到結果 → 解讀數據，用簡潔中文回覆
3. 如果查詢失敗 → 告知用戶稍後再試
```

**開發型 Agent（寫程式）：**
```markdown
---
inclusion: always
---

# X 社群爬蟲開發規格

## 技術要求
- 語言：Go 1.22+
- 瀏覽器控制：chromedp
- 資料庫：SQLite
- 不產生 exe，用 go run . 執行

## 開發順序
1. 資料庫 schema
2. 爬取核心邏輯
3. CLI 介面
4. 報告輸出
```

---

## 十、進階：Watchdog 與自動重啟

### Python Watchdog（開發用）

```bash
python scripts/watchdog.py
```

功能：
- 每 30 秒檢查 `/api/status`
- 服務掛掉時自動重啟
- 每小時最多重啟 5 次

### 啟動腳本（restart.flag 機制）

Agent 可以透過建立 `restart.flag` 檔案來請求重啟：

```bash
# Agent 內部可以這樣觸發重啟
echo "" > restart.flag
```

啟動腳本（`start-team.bat` / `start-team.sh`）會在程式退出後檢查這個檔案。

---

## 十一、故障排除

| 問題 | 原因 | 解法 |
|------|------|------|
| Agent 啟動失敗 | model 名稱錯誤 | `kiro-cli chat --list-models` 確認 |
| Port 衝突 | 上次未正常關閉 | 手動 kill 佔用 port 的程序 |
| 沒有回覆 | kiro-cli 卡住 | 檢查 Agent 的 stdout 輸出 |
| 回覆有亂碼 | ANSI escape 未過濾 | 已內建過濾，檢查是否有新格式 |
| 防毒刪除 exe | Go binary 被誤判 | 改用 `go run .`（已是預設） |
| Telegram 收不到訊息 | topic_id 錯誤 | 用 `scripts/get_ids.py` 確認 |
| 環境變數未載入 | .env 位置錯誤 | 確認 `.env` 在專案根目錄 |
| MCP tool 找不到 | mcp.json 設定錯誤 | 確認 command 路徑正確 |

### 常用除錯指令

```bash
# 確認 API 是否運行
curl http://127.0.0.1:8470/api/status

# 確認 kiro-cli 可用
kiro-cli whoami
kiro-cli chat --list-models

# 確認 Go 環境
go version
cd cmd/team && go build ./...   # 只檢查編譯，不產生 exe

# 確認 Telegram Bot
python scripts/get_ids.py
```

---

## 十二、專案結構總覽

```
KiroMultiAgent/
├── .env                          # 所有 secret（不進 git）
├── .env.example                  # 環境變數範本
├── .gitignore
├── team.yaml                     # 團隊設定（不進 git）
├── pyproject.toml                # Python 套件設定
│
├── cmd/team/                     # Go Team Manager（主程式）
│   ├── main.go                   # CLI 入口
│   ├── go.mod
│   └── internal/
│       ├── config/config.go      # team.yaml 載入
│       ├── daemon/               # Instance 生命週期管理
│       │   ├── daemon.go
│       │   └── ports.go          # Port 分配
│       ├── process/process.go    # kiro-cli subprocess 管理
│       ├── telegram/adapter.go   # Telegram 訊息路由
│       ├── api/api.go            # REST API
│       └── mcp/                  # MCP Server（Go 版）
│           ├── team.go           # 跨 Agent 通訊
│           └── hoyeah.go         # HoYeah API 查詢
│
├── src/kiro_multi_agent/         # Python 版（開發/備用）
│   ├── cli.py                    # CLI 入口
│   ├── config.py                 # team.yaml 載入
│   ├── daemon.py                 # Instance 管理
│   ├── process.py                # subprocess 管理
│   ├── backend.py                # kiro-cli 指令建構
│   ├── team.py                   # 高階協調
│   ├── telegram_adapter.py       # Telegram 路由
│   ├── api.py                    # REST API
│   ├── team_mcp.py              # Team MCP Server
│   └── hoyeah_mcp.py           # HoYeah MCP Server
│
├── agents/                       # Agent 工作目錄
│   ├── leader-agent/
│   └── {your-agents}/
│
├── templates/
│   └── agent-template/           # 新 Agent 模板（必須從這裡複製）
│       ├── .kiro/
│       │   ├── settings/mcp.json
│       │   └── steering/
│       │       ├── 00-agent-rules.md
│       │       ├── error-recovery.md
│       │       └── tech-stack.md
│       └── README.md
│
├── config/
│   └── ports.yaml                # Port 分配表
│
├── scripts/
│   ├── start-team.bat            # Windows 啟動腳本
│   ├── start-team.sh             # Linux/Mac 啟動腳本
│   ├── watchdog.py               # 健康監控
│   └── get_ids.py                # Telegram ID 取得工具
│
├── examples/
│   └── team.yaml                 # team.yaml 範例
│
├── docs/
│   ├── tutorial.md               # ← 本文件
│   ├── architecture.md           # 架構設計
│   └── multi-agent-complete-guide.md  # 完整技術文件
│
└── state/
    └── ports.json                # Runtime port 登記
```

---

## 附錄 A：Port 分配規則

| 範圍 | 用途 |
|------|------|
| 8470-8499 | Team 核心服務 |
| 8500-8599 | Agent 專用服務 |
| 8600-8699 | 工具/爬蟲服務 |
| 8700-8799 | 開發/測試用 |

所有 port 必須在 `config/ports.yaml` 登記後才能使用。

---

## 附錄 B：環境變數規範

| 規則 | 說明 |
|------|------|
| 集中管理 | 所有 secret 放在根目錄 `.env` |
| 不可 hardcode | 程式碼中不可出現任何 secret |
| 明確錯誤 | 未設定時回傳錯誤，不用 fallback |
| 單一來源 | Agent 目錄下不可有獨立 `.env` |
| MCP 引用 | 使用 `${VAR_NAME}` 語法 |

---

## 附錄 C：防毒軟體注意事項

Go 編譯的靜態 binary（10-30MB）會被 Norton 等防毒軟體誤判為惡意軟體。

**解法：不要用 `go build` 產生 exe，統一用 `go run .` 執行。**

```bash
# 正確
cd cmd/team && go run . team start

# 錯誤（會被防毒刪除）
go build -o team.exe . && ./team.exe
```

---

## 附錄 D：快速參考卡

```bash
# 安裝
pip install -e ".[dev]"

# 初始化
cp .env.example .env && cp examples/team.yaml team.yaml

# 建立新 Agent
cp -r templates/agent-template agents/my-agent

# 啟動
cd cmd/team && go run . team start

# 停止
Ctrl+C 或 go run . team stop

# 查看狀態
curl http://127.0.0.1:8470/api/status

# 取得 Telegram ID
python scripts/get_ids.py

# Watchdog（自動重啟）
python scripts/watchdog.py
```
