---
inclusion: always
---

# 技術選型規範（強制）

## Go 為主，Python 僅限 Multi-Agent 框架

### 強制規則

| 類型 | 語言 | 範例 |
|------|------|------|
| HTTP server / API | **Go** | REST API、webhook receiver |
| CLI 工具 | **Go** | 爬蟲、資料處理、自動化腳本 |
| 排程器 / Daemon | **Go** | watchdog、定時任務 |
| 爬蟲 / 資料蒐集 | **Go** | chromedp、HTTP client |
| Agent 任務產出的程式碼 | **Go** | 用戶要求開發的功能 |
| Multi-Agent 框架本身 | Python | daemon、telegram adapter、MCP server |
| MCP Server（team 通訊） | Python | team_mcp.py |

### 禁止事項
- ❌ 不可用 Python 開發新的 HTTP server
- ❌ 不可用 Python 開發 CLI 工具或爬蟲
- ❌ 不可用 Python 開發 watchdog 或排程器
- ❌ Agent 被指派開發任務時，不可預設用 Python（除非用戶明確要求）

### Go 專案結構
```
cmd/{project-name}/
├── main.go
├── go.mod
├── go.sum
└── internal/
    ├── config/
    ├── handler/
    └── ...
```

### 啟動方式
```bash
# 正確：用 go run 執行（避免防毒問題）
cd cmd/{project} && go run . {args}

# 錯誤：不要產生 exe
go build -o output.exe .
```

---

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
port := os.Getenv("SERVICE_PORT")

// 錯誤：寫死 port
port := "8080"
```

---

## 防毒安全規則（必須遵守）

### 規則
1. **不要用 `go build` 產生 exe 檔案**
2. 執行方式統一為 `go run .`
3. 如果必須產生 binary，先確認輸出目錄已加入防毒排除清單
4. 不要把 exe 檔案 commit 到 git
5. 使用 chromedp/網路操作的 Go 程式特別容易被誤判

### 原因
Go 編譯的靜態 binary（10-30MB）+ 瀏覽器控制行為會被 Norton 的 Heur.AdvML.D 啟發式偵測標記為惡意軟體。

---

## kiro-cli 啟動規範（必須遵守）

### 規則
1. **所有 kiro-cli instance 強制使用 `--legacy-ui` 模式**
2. 完整啟動參數：`kiro-cli chat --trust-all-tools --legacy-ui`
3. 不可切換到其他模式
4. 每個 instance 約佔 260MB 記憶體

### 記憶體管理
- 3 個 agent ≈ 780MB
- 5 個 agent ≈ 1.3GB
- 10 個 agent ≈ 2.6GB
- 如果記憶體不足，考慮「按需啟動」模式

---

## 環境變數規範

### 規則
1. 所有 API key、token、密碼必須放在根目錄 `.env`
2. 程式碼中不可 hardcode secret
3. Go 用 `os.Getenv()`，Python 用 `os.getenv()`
4. 未設定時回傳明確錯誤，不可用 fallback
5. Agent 目錄下不可有獨立 `.env`
