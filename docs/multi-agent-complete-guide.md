# Kiro Multi-Agent 完整技術文件

> 本文件涵蓋整個 Multi-Agent 系統的架構、規範、Agent 建立流程、Steering 機制，
> 以及所有必須遵守的開發規則。適合作為教學文件或新人上手指南。

---

## 目錄

1. [系統架構概覽](#一系統架構概覽)
2. [環境需求與安裝](#二環境需求與安裝)
3. [核心概念](#三核心概念)
4. [Steering 機制詳解](#四-steering-機制詳解)
5. [Agent 建立完整流程](#五-agent-建立完整流程)
6. [開發規範](#六開發規範)
7. [Port 管理機制](#七-port-管理機制)
8. [防毒軟體注意事項](#八防毒軟體注意事項)
9. [環境變數管理](#九環境變數管理)
10. [Telegram 整合](#十-telegram-整合)
11. [啟動與維運](#十一啟動與維運)
12. [故障排除](#十二故障排除)

---

## 一、系統架構概覽

```
┌─────────────────────────────────────────────────────┐
│                    Telegram Group                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Leader   │  │ HoYeahAPI│  │ X-Crawler│  ...     │
│  │ Topic    │  │ Topic    │  │ Topic    │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼──────────────┼──────────────┼───────────────┘
        │              │              │
┌───────▼──────────────▼──────────────▼───────────────┐
│              Go Team Manager (go run .)               │
│  ┌────────────────────────────────────────────────┐  │
│  │ TelegramAdapter (訊息路由 by topic_id)         │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ Daemon (kiro-cli subprocess 管理)              │  │
│  │  ├── leader-agent (kiro-cli instance)          │  │
│  │  ├── hoyeah-api  (kiro-cli instance)          │  │
│  │  └── x-crawler   (kiro-cli instance)          │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ REST API (port 8470)                           │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ Port Registry (state/ports.json)               │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### 訊息流程
1. 用戶在 Telegram Forum Topic 發訊息
2. TelegramAdapter 根據 topic_id 路由到對應 agent
3. 訊息寫入 kiro-cli 的 stdin
4. kiro-cli 處理後輸出到 stdout
5. 系統等待 `▸ Time:` 標記表示回覆完成
6. 過濾 ANSI/spinner 噪音，提取最終回覆
7. 回覆發送到 Telegram 對應 Topic

---

## 二、環境需求與安裝

### 必要軟體
| 軟體 | 版本 | 用途 |
|------|------|------|
| Go | 1.24+ | Team Manager 主程式 |
| Kiro CLI | 2.2+ | Agent 大腦（AI 推理引擎） |
| Python | 3.11+ | MCP Server（部分 agent） |
| Git | 任意 | 版本控制 |

### 安裝步驟
```bash
# 1. Clone 專案
git clone <repo-url>
cd KiroMutiAgent

# 2. 安裝 Python 依賴（MCP server 用）
pip install -e ".[dev]"

# 3. 確認 Go
go version

# 4. 確認 Kiro CLI
kiro-cli whoami
kiro-cli chat --list-models

# 5. 設定 .env
cp .env.example .env
# 編輯 .env 填入你的 token 和 API key

# 6. 啟動
cd cmd/team && go run . team start
```

---

## 三、核心概念

### Agent
一個 Agent 是一個獨立的 kiro-cli instance，有自己的：
- Working directory（`agents/{name}/`）
- Steering 檔案（行為規則）
- MCP Server（工具能力）
- Telegram Forum Topic（對話入口）

### Steering
Steering 是控制 Agent 行為的 Markdown 檔案，放在 `.kiro/steering/` 目錄下。
kiro-cli 啟動時會自動載入這些檔案作為系統指令。

### MCP Server
Model Context Protocol Server 提供 Agent 可呼叫的工具。
例如 `query_hoyeah` 讓 agent 能查詢營運數據。

### Team Manager
Go 程式，負責：
- 啟動/停止所有 kiro-cli instance
- Telegram 訊息路由
- REST API
- Port 管理
- 健康檢查與自動重啟

---

## 四、Steering 機制詳解

### 層級結構
```
.kiro/steering/              ← Workspace 級（所有人都看得到）
  ├── coding-rules.md        ← 程式碼規範
  ├── structure.md           ← 專案結構
  ├── tech.md                ← 技術棧
  ├── agent-creation.md      ← Agent 建立準則
  └── security-notes.md      ← 安全注意事項

agents/{name}/.kiro/steering/ ← Agent 級（只有該 agent 看得到）
  ├── 00-agent-rules.md      ← 核心行為規則（from template）
  ├── error-recovery.md      ← 錯誤處理 SOP（from template）
  ├── tech-stack.md          ← 技術選型 + port/防毒規則（from template）
  ├── language.md            ← 回覆語言設定
  └── {custom}.md            ← Agent 專屬規格書
```

### Steering 檔案格式
```markdown
---
inclusion: always
---

# 標題

內容...
```

`inclusion: always` 表示每次對話都會載入。

### Template 提供的基礎 Steering

| 檔案 | 內容 | 可否修改 |
|------|------|---------|
| 00-agent-rules.md | 進度回報、程式原則、錯誤處理、回覆風格 | 可覆蓋 |
| error-recovery.md | L1/L2/L3 錯誤分級、重試策略 | 不可刪除 |
| tech-stack.md | Go/Python 選型、Port 規則、防毒規則 | 不可刪除 |

### 自訂 Steering 範例

**營運數據查詢 Agent：**
```markdown
---
inclusion: always
---

# HoYeah API Agent - 營運數據查詢

## 角色定義
你是營運數據查詢助手...

## 對話策略
1. 使用 query_hoyeah tool 查詢
2. 收到數據後解讀分析
...
```

**開發型 Agent：**
```markdown
---
inclusion: always
---

# X 社群爬蟲工具規格書

## 技術要求
- 語言：Go 1.24+
- 專案位置：tools/x-community-insight/
...
```

---

## 五、Agent 建立完整流程

### 前置條件
- Team Manager 已能正常運行
- Telegram Bot 有管理員權限（含管理話題）
- `.env` 已設定好

### 步驟一：從 Template 複製

```bash
cp -r templates/agent-template agents/{new-agent-name}
```

**⚠️ 必須從 template 複製，不可手動建立。**

複製後的結構：
```
agents/{new-agent-name}/
├── .kiro/
│   ├── settings/
│   │   └── mcp.json          ← 需修改
│   ├── skills/
│   └── steering/
│       ├── 00-agent-rules.md  ← 可覆蓋
│       ├── error-recovery.md  ← 不可刪除
│       └── tech-stack.md      ← 不可刪除
├── logs/
│   └── .gitkeep
└── README.md
```

### 步驟二：修改 MCP 設定

編輯 `agents/{name}/.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "team": {
      "command": "go",
      "args": ["run", "./cmd/team", "mcp", "team",
        "--port", "8470",
        "--instance", "{agent-name}",
        "--role", "worker"
      ]
    }
  }
}
```

替換：
- `{agent-name}` → 你的 agent 名稱
- `role` → `worker` 或 `leader`

如需額外 MCP server（如 hoyeah），加入對應設定，env 用 `${VAR_NAME}` 引用。

### 步驟三：加入 Language Steering

建立 `agents/{name}/.kiro/steering/language.md`：

```markdown
---
inclusion: always
---

# 語言規則

## 回覆語言
- 一律使用繁體中文回覆
- 技術術語可保留英文，但說明用繁體中文
- 不使用簡體中文
```

### 步驟四：加入專屬 Steering

根據 agent 類型建立專屬 steering 檔案：

- 對話型 agent → 定義角色、對話策略、能力邊界
- 開發型 agent → 完整規格書（技術棧、專案結構、MVP 順序）
- 查詢型 agent → API 使用方式、回覆格式

### 步驟五：建立 Telegram Forum Topic

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
r = requests.post(
    f"https://api.telegram.org/bot{token}/createForumTopic",
    json={"chat_id": -1003914684222, "name": "{Topic-Name}"}
)
print(r.json())  # 記下 message_thread_id
```

或使用 `scripts/get_ids.py` 監聽取得。

### 步驟六：更新 team.yaml

```yaml
instances:
  {agent-name}:
    working_directory: ./agents/{agent-name}
    description: "描述"
    topic_id: {從步驟五取得}
    role: worker
```

### 步驟七：重啟 Team

```bash
# 停止
Ctrl+C

# 重新啟動
cd cmd/team && go run . team start
```

### 步驟八：驗證

在 Telegram 對應 Topic 發訊息，確認 agent 有回覆。

---

## 六、開發規範

### 環境變數規範
| 規則 | 說明 |
|------|------|
| Secret 集中管理 | 所有 API key、token、URL 放在根目錄 `.env` |
| 不可 hardcode | 程式碼中不可出現任何 secret |
| 明確錯誤 | 未設定時回傳錯誤訊息，不用 fallback |
| 單一來源 | Agent 目錄下不可有獨立 `.env` |
| MCP env 引用 | 使用 `${VAR_NAME}` 語法 |

### 程式碼規範
| 規則 | Go | Python |
|------|-----|--------|
| 讀取 env | `os.Getenv("KEY")` | `os.getenv("KEY")` |
| Port | 從 config 讀取 | 從 config 讀取 |
| 執行方式 | `go run .` | `python -m module` |
| 不可產生 | `.exe` 檔案 | — |

### 命名規範
| 元素 | 風格 | 範例 |
|------|------|------|
| Agent 目錄 | kebab-case | `hoyeah-api` |
| Steering 檔案 | kebab-case.md | `hoyeah-api.md` |
| Go package | lowercase | `daemon` |
| Go function | PascalCase | `StartInstance()` |
| Config key | snake_case | `topic_id` |

---

## 七、Port 管理機制

### 分配規則
| 範圍 | 用途 |
|------|------|
| 8470-8499 | Team 核心服務 |
| 8500-8599 | Agent 專用服務 |
| 8600-8699 | 工具/爬蟲服務 |
| 8700-8799 | 開發/測試用 |

### 設定檔位置
`config/ports.yaml`

### 運作機制
1. **開發階段**：agent 寫程式碼時必須查閱 `config/ports.yaml`
2. **啟動階段**：Port Registry 檢查 port 是否被佔用
3. **執行階段**：分配記錄寫入 `state/ports.json`
4. **關閉階段**：釋放 port 登記

### 新增 Port 流程
1. 在 `config/ports.yaml` 登記
2. 在程式碼中從設定檔讀取（不可寫死）
3. 啟動時由 Port Registry 驗證

---

## 八、防毒軟體注意事項

### 問題
Go 編譯的靜態 binary（10-30MB）會被 Norton 等防毒軟體的啟發式偵測標記為惡意軟體（`Heur.AdvML.D`）。

### 原因
- Go 把整個 runtime 打包成大型 binary
- chromedp/網路操作行為模式類似惡意軟體
- 本地編譯的 exe 沒有數位簽章
- 信譽系統無法驗證來源

### 規則
1. **不要用 `go build` 產生 exe**
2. 統一用 `go run .` 從原始碼執行
3. 不要把 exe commit 到 git
4. 如果必須產生 binary，先加入防毒排除清單

### 啟動指令
```bash
# 正確
cd cmd/team && go run . team start

# 錯誤（會產生 exe）
go build -o kiro-team.exe . && ./kiro-team.exe team start
```

---

## 九、環境變數管理

### .env 檔案
位置：專案根目錄 `.env`（已在 .gitignore 中）

```env
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# HoYeah API
HOYEAH_API_BASE=http://192.168.132.54:8642/v1/
HOYEAH_API_KEY=your_api_key_here

# 未來新增的 API 都放這裡
# X_API_KEY=...
# OPENAI_API_KEY=...
```

### 載入機制
- Go：`github.com/joho/godotenv` 在 main.go 載入
- Python：`python-dotenv` 的 `load_dotenv()`
- MCP server：透過 mcp.json 的 `env` 區塊傳遞

### 新增環境變數流程
1. 在 `.env` 加入新變數
2. 在 `.env.example` 加入範例（不含實際值）
3. 在程式碼中用 `os.Getenv()` 讀取
4. 未設定時回傳明確錯誤

---

## 十、Telegram 整合

### Bot 設定
- Bot 需要管理員權限（含管理話題）
- 群組需開啟 Forum Topics

### 訊息路由
```
Forum Topic (topic_id) → team.yaml instances → kiro-cli stdin
```

### 支援的訊息類型
| 類型 | 處理方式 |
|------|---------|
| 文字 | 直接送入 agent stdin |
| 圖片 | 下載到 media/{instance}/，傳路徑給 agent |
| 檔案 | 下載到 media/{instance}/，傳路徑+檔名給 agent |

### 回覆機制
- 長文字自動分割（4096 字元限制）
- 優先在換行處切割
- 過濾 ANSI escape codes 和 spinner 動畫
- 等待 `▸ Time:` 標記確認回覆完成
- 15 分鐘 timeout

### 權限控制
`team.yaml` 的 `access.allowed_users` 列表控制誰能使用 bot。

---

## 十一、啟動與維運

### 啟動
```bash
cd cmd/team && go run . team start
```

### 停止
- 在終端按 `Ctrl+C`
- 或執行 `go run . team stop`

### 查看狀態
```bash
# CLI
go run . team status

# API
curl http://127.0.0.1:8470/api/status
```

### 日誌
啟動後直接在終端輸出，格式：
```
HH:MM:SS [module] message
```

### 健康檢查
- 每 30 秒檢查 kiro-cli instance 是否存活
- 崩潰時自動重啟（指數退避，最多 10 次）

---

## 十二、故障排除

| 問題 | 原因 | 解法 |
|------|------|------|
| Agent 啟動失敗 | model 名稱錯誤 | `kiro-cli chat --list-models` 確認 |
| Port 衝突 | 上次未正常關閉 | 手動 kill 佔用 port 的程序 |
| 沒有回覆 | handler 阻塞 | 確認用 goroutine 非阻塞處理 |
| 回覆有亂碼 | ANSI escape 未過濾 | 檢查 StripANSI 函數 |
| 回覆是 JSON | idle timeout 太短 | 等待 `▸ Time:` 標記 |
| 防毒刪除 exe | Go binary 被誤判 | 改用 `go run .` |
| MCP tool 找不到 | mcp.json 被覆蓋 | 確認 merge 模式 |
| Telegram 收不到訊息 | topic_id 錯誤 | 用 get_ids.py 確認 |
| 環境變數未載入 | .env 位置錯誤 | 確認在專案根目錄 |

---

## 附錄：檔案結構總覽

```
KiroMutiAgent/
├── .env                          # 所有 secret（不進 git）
├── .gitignore
├── team.yaml                     # 團隊設定
├── .kiro/
│   ├── hooks/                    # IDE hooks
│   └── steering/                 # Workspace 級規範
│       ├── coding-rules.md
│       ├── structure.md
│       ├── tech.md
│       ├── agent-creation.md
│       └── security-notes.md
├── cmd/
│   └── team/                     # Go Team Manager
│       ├── main.go
│       ├── go.mod
│       └── internal/
│           ├── config/
│           ├── daemon/
│           ├── process/
│           ├── telegram/
│           ├── api/
│           └── mcp/
├── agents/
│   ├── leader-agent/
│   ├── hoyeah-api/
│   └── x-crawler/
├── templates/
│   └── agent-template/           # Agent 建立模板
├── config/
│   └── ports.yaml                # Port 分配表
├── state/
│   └── ports.json                # Runtime port 登記
├── docs/
│   ├── setup-guide.md
│   ├── create-dev-agent-guide.md
│   └── multi-agent-complete-guide.md  ← 本文件
└── scripts/
    └── get_ids.py                # Telegram ID 取得工具
```
