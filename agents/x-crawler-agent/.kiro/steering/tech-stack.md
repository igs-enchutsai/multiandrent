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

## kiro-cli 啟動規範（必須遵守）

### 規則
1. **所有 kiro-cli instance 預設使用 `--legacy-ui` 模式**
2. 完整啟動參數：`kiro-cli chat --trust-all-tools --legacy-ui`
3. 切換到其他模式前，必須先詢問用戶並說明差異
4. 每個 instance 約佔 260MB 記憶體，規劃 agent 數量時需考慮

### UI 模式差異

| 模式 | 參數 | 記憶體 | stdout 格式 | 適用場景 |
|------|------|--------|------------|---------|
| Legacy UI | `--legacy-ui` | 較低 (~260MB) | 純文字 + ANSI，可解析 | **預設，Multi-Agent 用** |
| TUI | `--tui` | 較高 | 複雜 TUI 渲染，難解析 | 人工互動終端機 |
| 無指定 | (無) | 較高 | 預設 TUI | 不建議用於 subprocess |

### 何時需要切換模式
- 如果未來 kiro-cli 更新導致 `--legacy-ui` 的 stdout 格式改變
- 如果需要特殊的 TUI 功能（如即時串流顯示）
- 切換前必須確認新模式的 stdout 能被 process.go 正確解析

### 記憶體管理
- 3 個 agent ≈ 780MB
- 5 個 agent ≈ 1.3GB
- 10 個 agent ≈ 2.6GB
- 如果記憶體不足，考慮「按需啟動」模式（閒置 agent 自動停止）
