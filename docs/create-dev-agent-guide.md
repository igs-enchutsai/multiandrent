# 開發型 Agent 建立手冊

透過 Telegram 指揮 AI Agent 在 workspace 中撰寫程式碼。

---

## 概念

「開發型 Agent」是一種特殊的 agent，它的工作不是回答問題或查資料，而是**在你的 workspace 中寫程式碼**。你透過 Telegram 對話下指令，agent 會根據 steering 裡的規格書，逐步完成整個專案。

```
你（Telegram）→ 下指令 → Agent（kiro-cli）→ 在 workspace 寫程式碼
```

---

## 建立流程

### 第一步：準備需求文件

把你的專案需求寫成一份完整的規格書，包含：

- 技術棧（語言、框架、資料庫）
- 專案結構
- 核心功能描述
- 資料庫 Schema
- CLI 指令設計
- MVP 優先順序

**重點：指定用什麼語言寫。** 例如「用 Go 撰寫」或「用 TypeScript 撰寫」。

### 第二步：建立 Agent 目錄

從 template 複製：

```bash
cp -r templates/agent-template agents/{agent-name}
```

### 第三步：修改 MCP 設定

編輯 `agents/{agent-name}/.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "team": {
      "command": "python",
      "args": [
        "-m", "kiro_multi_agent.team_mcp",
        "--port", "8470",
        "--instance", "{agent-name}",
        "--role", "worker",
        "--allowed-targets", ""
      ]
    }
  }
}
```

### 第四步：加入 Steering 檔案

在 `agents/{agent-name}/.kiro/steering/` 加入：

1. **language.md** — 指定回覆語言（繁體中文）
2. **{agent-name}-spec.md** — 你的需求規格書（最重要）

#### language.md 範本
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

#### 規格書 steering 範本
```markdown
---
inclusion: always
---

# {專案名稱} 規格書

## 技術要求
- 語言：Go 1.24+
- 專案位置：tools/{project-name}/

## 專案結構
（列出目錄結構）

## 核心功能
（描述每個模組要做什麼）

## MVP 優先順序
1. ...
2. ...
3. ...
```

### 第五步：覆蓋 00-agent-rules.md

把 template 的通用規則替換為開發型 agent 的規則：

```markdown
---
inclusion: always
---

# Agent Core Rules

## 1. 角色定義
你是 {專案名稱} 開發 Agent。你的工作是根據需求規格書，
在 workspace 中用 {語言} 撰寫程式碼。

## 2. 技術棧
- 語言：{Go/TypeScript/Python}
- 專案位置：tools/{project-name}/

## 3. 工作模式
- 收到指令後，在指定目錄下撰寫程式碼
- 每完成一個模組就回報進度
- 遇到問題主動說明並提出替代方案
- 程式碼要能編譯通過才算完成

## 4. 回覆風格
- 簡潔回報進度
- 完成時列出已建立的檔案
- 遇到阻礙時說明原因和建議
```

### 第六步：建立 Telegram Topic

用 Bot API 建立（需要 bot 有管理話題權限）：

```python
import requests
token = "YOUR_BOT_TOKEN"
r = requests.post(
    f"https://api.telegram.org/bot{token}/createForumTopic",
    json={"chat_id": YOUR_GROUP_ID, "name": "{Agent-Name}"}
)
print(r.json())  # 取得 message_thread_id
```

### 第七步：更新 team.yaml

```yaml
instances:
  {agent-name}:
    working_directory: ./agents/{agent-name}
    description: "{描述}"
    topic_id: {從上一步取得的 ID}
    role: worker
```

### 第八步：重啟 Team

```bash
./bin/kiro-team.exe team start
```

---

## 使用方式

在 Telegram 的對應 Topic 中發送指令：

### 初始化階段
```
建立專案結構和 go.mod
```

### 逐步開發
```
實作 SQLite schema 和 migration
```
```
實作 CLI 框架（cobra）
```
```
實作貼文爬取模組
```
```
實作留言蒐集（多輪滾動、去重）
```

### 除錯
```
編譯看看有沒有錯誤
```
```
修正 XXX 模組的 bug
```

### 查看進度
```
目前完成了哪些模組？還有什麼沒做？
```

---

## 最佳實踐

### 1. 指令要具體
❌ 「把專案做完」
✅ 「實作 database/repository.go，包含 posts 和 replies 的 CRUD」

### 2. 一次一個模組
不要一次要求做太多事。一個指令完成一個模組，確認沒問題再繼續。

### 3. 要求編譯驗證
每完成一個模組，要求 agent 執行 `go build ./...` 確認能編譯。

### 4. 規格書要完整
steering 裡的規格書越詳細，agent 的產出品質越高。
包含具體的：
- 資料結構定義
- 函數簽名
- 錯誤處理策略
- 輸出格式範例

### 5. 善用 MVP 優先順序
在規格書裡明確標示 MVP 順序，agent 會按順序實作。

---

## 範例：X 社群爬蟲 Agent

| 項目 | 值 |
|------|-----|
| Agent 名稱 | x-crawler |
| Telegram Topic | X-Crawler |
| 技術棧 | Go + chromedp + SQLite |
| 專案輸出位置 | tools/x-community-insight/ |
| Steering 檔案 | x-crawler-spec.md（完整規格書） |

指令範例：
1. 「建立 tools/x-community-insight/ 的專案結構和 go.mod」
2. 「實作 SQLite schema，建立 10 張表」
3. 「實作 chromedp 貼文頁爬取」
4. 「實作留言多輪蒐集與去重」
5. 「實作 Markdown 報告匯出」
6. 「寫 README」

---

## 適用場景

這種模式適合：
- 有明確規格的工具開發
- 需要逐步迭代的專案
- 想透過對話控制開發節奏
- 不想自己寫但想掌控方向

不適合：
- 需要即時互動的服務（用一般 agent）
- 純粹查資料或回答問題（用 HoYeah API 類型）
- 需要存取外部系統的即時操作
