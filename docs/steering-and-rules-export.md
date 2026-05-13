# Kiro Multi-Agent Steering & 準則匯出

> 本文件匯出所有 Steering 檔案、準則、知識庫內容。
> 可直接提供給其他 Multi-Agent 系統學習使用。

---

## 一、Workspace 級 Steering（全域規範）

以下規則對所有 agent 生效。

---

### 1. coding-rules.md — 程式碼規範

```markdown
---
inclusion: always
---

# Coding Rules

## Naming
| Element | Style | Example |
|---------|-------|---------|
| Module | snake_case.py | team_mcp.py |
| Class | PascalCase | TeamManager |
| Function | snake_case | start_instance() |
| Constant | UPPER_SNAKE | READY_PATTERN |
| Enum member | UPPER_SNAKE | InstanceStatus.RUNNING |

## Style
- Every .py starts with docstring + from __future__ import annotations
- All public functions must have type annotations
- Use dataclass for config/state, not dict
- asyncio for all I/O operations
- Logging: log = logging.getLogger(__name__), use %s format

## Safety
- YAML: always yaml.safe_load() (never yaml.load())
- Tokens from env vars, never hardcoded
- .env must be in .gitignore

## 環境變數規範（必須遵守）

### 規則
1. **所有 API key、token、密碼、外部服務 URL 必須放在根目錄 `.env`**
2. 程式碼中不可出現任何 hardcoded 的 secret 或外部服務位址
3. 讀取方式：透過 `os.Getenv()` (Go) 或 `os.getenv()` (Python)
4. 未設定時應回傳明確錯誤訊息，不可用 hardcoded fallback
5. Agent 目錄下不可有獨立的 `.env` 檔案，統一由根目錄管理
6. MCP server 的 env 區塊使用 `${VAR_NAME}` 語法引用環境變數

### .env 檔案位置
- 唯一位置：專案根目錄 `.env`
- 已在 `.gitignore` 中排除

### 範例
```go
// 正確
apiKey := os.Getenv("HOYEAH_API_KEY")
if apiKey == "" {
    return "錯誤：未設定 HOYEAH_API_KEY"
}

// 錯誤
apiKey := "71ae11c594ad..."
```
```

---

### 2. agent-creation.md — Agent 建立準則

```markdown
---
inclusion: always
---

# Agent 建立準則

## 必須從 Template 複製

建立新 agent 時，**必須**從 `templates/agent-template/` 複製完整結構，然後再修改。

### 步驟
1. 複製 `templates/agent-template/` 到 `agents/{new-agent-name}/`
2. 修改 `.kiro/settings/mcp.json`：
   - 替換 `__AGENT_NAME__` 為 agent 名稱
   - 替換 `role` 為 worker 或 leader
   - 如需額外 MCP server，加入對應設定
3. 保留所有 template steering 檔案（不可刪除）：
   - `00-agent-rules.md` — 核心行為規則
   - `error-recovery.md` — 錯誤處理 SOP
   - `tech-stack.md` — 技術選型指南
4. 加入 `language.md` — 指定繁體中文回覆
5. 加入該 agent 專屬的 steering 檔案
6. 在 Telegram 建立 Forum Topic
7. 更新 `team.yaml` 加入新 instance
8. 重啟 team

### 禁止事項
- 不可跳過 template 直接手動建立 agent 目錄
- 不可刪除 template 中的任何 steering 檔案
- 不可省略 `error-recovery.md`（所有 agent 都需要錯誤處理能力）

### Template 包含的基礎能力
| 檔案 | 提供的能力 |
|------|-----------|
| 00-agent-rules.md | 進度回報、程式原則、錯誤處理、Telegram 回覆風格 |
| error-recovery.md | L1/L2/L3 錯誤分級、重試策略 |
| tech-stack.md | Go/Python 技術選型指南 |
```

---

### 3. security-notes.md — 安全與防毒注意事項

```markdown
---
inclusion: always
---

# 安全與防毒注意事項

## Go 編譯 exe 會被防毒軟體誤判

### 事件紀錄（2026-05-10）
- Norton 偵測 `Heur.AdvML.D`（啟發式機器學習偵測）
- 檔案：x-insight.exe（Go 編譯的 binary，24MB）
- 原因：Go 靜態連結 + chromedp 瀏覽器控制行為 + 無數位簽章 + 信譽不足
- 結果：檔案被自動刪除

### 規則
1. **不要用 `go build` 產生 exe 檔案**，改用 `go run .` 直接從原始碼執行
2. 如果必須產生 exe，先把輸出目錄加入防毒排除清單
3. 啟動指令統一為：`cd cmd/{project} && go run . {args}`
4. 不要把 exe 檔案 commit 到 git

### 為什麼 Go exe 會被誤判
- Go 把整個 runtime 打包成大型靜態 binary（10-30MB）
- 使用 chromedp/網路操作的程式行為模式類似惡意軟體
- 本地編譯的 exe 沒有數位簽章，信譽系統無法驗證
- Norton 的 `Heur.AdvML.D` 是機器學習模型判斷，不是特徵碼比對

### 影響範圍
- cmd/team（kiro-team.exe）
- tools/x-community-insight（x-insight.exe）
- 任何未來用 Go 編譯的工具
```

---

## 二、Agent Template Steering（每個 Agent 繼承）

以下是 `templates/agent-template/.kiro/steering/` 中的檔案，所有新建 agent 都會繼承。

---

### 1. 00-agent-rules.md — 核心行為規則

```markdown
---
inclusion: always
---

# Agent Core Rules

## 1. Progress Reporting (Mandatory)

Report progress every 5 minutes during task execution.

### When to Report
1. Task start: "Starting XXX"
2. Every 5 minutes: current progress
3. On error: immediately
4. On completion: result summary

## 2. Coding Principles

- Think before coding. State assumptions explicitly.
- Simplicity first. Minimum code to solve the problem.
- Surgical edits. Only change what is necessary.
- Goal-driven. Define success criteria, iterate until verified.

## 3. Error Handling

- Retry up to 3 times with exponential backoff
- Use `log_to_leader()` for internal errors (not visible to user)
- Never show raw stack traces to users
- Always provide alternative approaches when blocked

## 4. Telegram Reply Style

- Concise: max 300 chars per message
- Result-oriented: conclusion first, then reasoning
- Use emoji prefixes: success, warning, progress, info
- Never paste raw stdout, diffs, or JSON to users
```

---

### 2. error-recovery.md — 錯誤處理 SOP

```markdown
---
inclusion: always
---

# Error Recovery

| Level | Definition | Action |
|-------|-----------|--------|
| L1 Minor | Single operation failed | Auto-retry (max 3) |
| L2 Medium | Dependency temporarily unavailable | Wait 30s, notify leader |
| L3 Severe | Core function broken | Notify leader + user, stop |

## Retry Strategy
- Attempt 1: wait 3s
- Attempt 2: wait 10s
- Attempt 3: wait 30s
- All failed: escalate to L2
```

---

### 3. tech-stack.md — 技術選型 + Port + 防毒規則

```markdown
---
inclusion: always
---

# Technology Guidelines

## Go First, Python Assist

- New HTTP servers, CLI tools, schedulers -> Go
- Telegram Bot, Kiro CLI management, MCP -> Python
- Do not use Python for new HTTP servers or watchdogs

## Port 管理規則（必須遵守）

### 規則
1. **任何需要監聽 port 的服務，必須先查閱 `config/ports.yaml`**
2. 不可自行選擇 port，必須從分配表中取得
3. 如果需要新 port，必須先在 `config/ports.yaml` 登記後才能使用
4. 開發階段寫程式碼時，port 必須從設定檔讀取，不可寫死

### Port 分配表位置
`config/ports.yaml`

### 程式碼中使用 port 的方式
```go
// 正確：從設定檔或環境變數讀取
port := cfg.HealthPort

// 錯誤：寫死 port
port := 8470
```

## 防毒安全規則（必須遵守）

### 規則
1. **不要用 `go build` 產生 exe 檔案**
2. 執行方式統一為 `go run .`
3. 如果必須產生 binary，先確認輸出目錄已加入防毒排除清單
4. 不要把 exe 檔案 commit 到 git
5. 使用 chromedp/網路操作的 Go 程式特別容易被誤判

### 原因
Go 編譯的靜態 binary（10-30MB）+ 瀏覽器控制行為會被 Norton 的 Heur.AdvML.D 啟發式偵測標記為惡意軟體。
```

---

## 三、Port 分配表

```yaml
# Port 分配表
# 所有 agent 開發時需要使用 port 必須先在此登記
# 不可自行選擇 port，避免衝突
#
# 規則：
# - 8470-8499: team 核心服務
# - 8500-8599: agent 專用服務
# - 8600-8699: 工具/爬蟲服務
# - 8700-8799: 開發/測試用

services:
  team-api:
    port: 8470
    owner: team
    purpose: "REST API + 跨 agent 通訊"
    status: active

  x-insight-web:
    port: 8600
    owner: x-crawler
    purpose: "X Community Insight Web UI"
    status: reserved

  hoyeah-proxy:
    port: 8642
    owner: external
    purpose: "HoYeah API (外部服務，不可佔用)"
    status: external

  dev-test:
    port: 8700
    owner: development
    purpose: "開發測試用"
    status: reserved

external:
  - port: 8642
    note: "HoYeah API (192.168.132.54)"
```

---

## 四、知識庫：踩坑紀錄與解法

### kiro-cli subprocess 管理

| 問題 | 原因 | 解法 |
|------|------|------|
| stdout 讀不到 | kiro-cli 用 `\r` 更新 TUI | 用 chunk-based `read(4096)` 不用 `readline()` |
| 回覆有 ANSI 亂碼 | 終端控制碼 + spinner | regex 過濾 `\x1b[...]` + braille chars |
| 回覆是 tool JSON | idle timeout 太短 | 等待 `▸ Time:` 結束標記 |
| handler 阻塞 | await 等回覆卡住 event loop | 用 goroutine/asyncio.create_task 非阻塞 |
| MCP config 被覆蓋 | write_config 每次覆寫 | 改為 merge 模式（只更新 team server） |
| model 不存在 | team.yaml 用了舊名稱 | `kiro-cli chat --list-models` 確認 |

### Telegram Bot

| 問題 | 原因 | 解法 |
|------|------|------|
| 收不到 Forum Topic 訊息 | go-telegram-bot-api 不支援 thread_id | 用原生 HTTP API |
| Bot 沒權限建 Topic | 缺少管理話題權限 | 給 bot 管理員 + 管理話題 |
| 訊息超過 4096 字 | Telegram 限制 | 自動分割（優先在換行處切） |

### Go 編譯

| 問題 | 原因 | 解法 |
|------|------|------|
| exe 被防毒刪除 | Heur.AdvML.D 誤判 | 改用 `go run .` |
| `cmd /c` 路徑錯誤 | 引號處理問題 | 直接用 `exec.Command(binary, args...)` |
| go run 找不到 module | 不在 module 目錄 | `cd cmd/team && go run .` |

### Port 管理

| 問題 | 原因 | 解法 |
|------|------|------|
| port 衝突 | 上次未正常關閉 | Port Registry + 啟動時清理 stale |
| agent 寫死 port | 沒有查分配表 | steering 規範 + config/ports.yaml |

---

## 五、.env 範本

```env
# ═══════════════════════════════════════
# Kiro Multi-Agent 環境變數
# 所有 secret 統一放在此檔案
# 此檔案不可 commit 到 git
# ═══════════════════════════════════════

# ─── Telegram ───
TELEGRAM_BOT_TOKEN=your_bot_token_here

# ─── HoYeah API ───
HOYEAH_API_BASE=http://192.168.132.54:8642/v1/
HOYEAH_API_KEY=your_api_key_here

# ─── 未來擴充 ───
# OPENAI_API_KEY=
# CLAUDE_API_KEY=
# X_BEARER_TOKEN=

# ─── 系統設定 ───
# KIRO_MULTI_AGENT_HOME=/path/to/home
```

---

## 六、team.yaml 範本

```yaml
channel:
  bot_token_env: TELEGRAM_BOT_TOKEN
  group_id: -1003914684222
  general_topic_id: 1

access:
  mode: locked
  allowed_users: [966434356]

defaults:
  backend: kiro-cli
  model: claude-sonnet-4

cost_guard:
  daily_limit_usd: 10.0
  warn_at_percentage: 80
  timezone: UTC

hang_detector:
  enabled: true
  timeout_minutes: 60

instances:
  leader-agent:
    working_directory: ./agents/leader-agent
    description: "Team leader - task coordination"
    topic_id: 6
    role: leader
    general_topic: true

  hoyeah-api:
    working_directory: ./agents/hoyeah-api
    description: "營運數據查詢 - HoYeah API"
    topic_id: 9
    role: worker

  x-crawler:
    working_directory: ./agents/x-crawler
    description: "X社群爬蟲開發"
    topic_id: 38
    role: worker

health_port: 8470
```

---

## 七、快速參考卡

### 啟動系統
```bash
cd cmd/team && go run . team start
```

### 建立新 Agent
```bash
cp -r templates/agent-template agents/{name}
# 修改 mcp.json、加入 steering、建立 Topic、更新 team.yaml、重啟
```

### 查看狀態
```bash
curl http://127.0.0.1:8470/api/status
```

### 新增 Port
1. 編輯 `config/ports.yaml`
2. 程式碼中從 config 讀取
3. 不可寫死

### 新增環境變數
1. 加入 `.env`
2. 加入 `.env.example`（不含實際值）
3. 程式碼用 `os.Getenv()` 讀取
