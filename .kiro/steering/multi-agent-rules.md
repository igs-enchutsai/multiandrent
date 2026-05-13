---
inclusion: always
---

# Multi-Agent 系統規範（經驗教訓整理）

本文件整理自實際開發過程中遇到的問題與修正，所有 agent 和開發者必須遵守。

---

## 1. 語言規範（強制）

- **一律使用繁體中文回覆**，無例外
- 所有回覆、說明、摘要、錯誤訊息都必須是繁體中文
- 技術術語可保留英文原文，但前後說明必須用繁體中文
- 即使用戶用英文提問，也用繁體中文回覆
- 禁止整段英文回覆

---

## 2. Telegram Forum Topic 規範（強制）

### 規則
- **每個 Agent 必須有獨立的 Forum Topic**
- 不可讓多個 Agent 共用同一個 Topic
- 沒有 topic_id 不可完成 Agent 建立流程
- Leader Agent 可使用 `create_forum_topic()` 工具自動建立 Topic

### 建立流程
1. 使用 `create_forum_topic(name="agent-name", instance="agent-name")`
2. 取得回傳的 topic_id
3. 寫入 `team.yaml`
4. 呼叫 `restart_team()` 載入新配置

---

## 3. MCP Server 與 API 規範

### `from __future__ import annotations` 相容性問題

⚠️ **嚴重問題：FastAPI + Pydantic + `from __future__ import annotations` 不相容**

- 當使用 `from __future__ import annotations` 時，所有 type annotation 變成字串（延遲評估）
- FastAPI 無法在 runtime 解析函數內部定義的 Pydantic BaseModel
- **解法：Pydantic model 必須定義在模組層級（module-level），不可定義在函數內部**

```python
# ✅ 正確：模組層級定義
from pydantic import BaseModel

class ReplyRequest(BaseModel):
    instance: str
    text: str

# ❌ 錯誤：函數內部定義（會導致 422 Unprocessable Content）
async def start(self):
    class ReplyRequest(BaseModel):  # FastAPI 找不到這個 class
        instance: str
        text: str
```

### MCP Tool 呼叫 API 的注意事項
- MCP server 是獨立 process，透過 HTTP 呼叫 daemon API
- API 必須在 daemon 啟動後才能使用
- 如果 API 返回 422，表示 Pydantic model 解析失敗（見上方）

---

## 4. kiro-cli stdin/stdout 規範

### 輸入（stdin）
- kiro-cli 的 chat 模式是 **line-based**（一行一個輸入）
- **多行文字必須 flatten 成單行**再送入 stdin
- 使用 `text.replace("\n", " ↵ ")` 將換行轉為可見符號
- 檔案路徑和 caption 用 ` | ` 分隔，不可用 `\n`

```python
# ✅ 正確
flat_text = text.replace("\n", " ↵ ").replace("\r", "")
await process.send_input(flat_text)

# ❌ 錯誤：多行文字會被拆成多個獨立輸入
await process.send_input("[FILE: path]\ncaption text")
```

### 輸出（stdout）偵測
- 回應完成的標記：`▸ Time:` 或 `Time:`
- 長任務（建立 agent、讀取大檔案）可能需要 3-10 分鐘
- 必須有 timeout 機制（預設 15 分鐘）
- 超時後回傳已收集的內容或錯誤訊息

### Agent 使用 reply tool 的行為
- Agent 可能使用 MCP `reply()` tool 直接回覆 Telegram
- 此時 stdout 的回應只是 tool call 的 artifact（如 "sent"）
- `_process_and_reply` 不應重複發送已透過 reply tool 發出的訊息

---

## 5. 檔案路徑規範

### 問題背景
- Telegram adapter 的 CWD 是 daemon 啟動目錄（如 `src/`）
- kiro-cli 的 CWD 是 agent 的 working_directory（如 `src/agents/leader-agent/`）
- 相對路徑在兩者之間不通用

### 規則
- **傳給 agent 的檔案路徑必須使用絕對路徑**
- 使用 `path.resolve()` 取得絕對路徑
- 媒體檔案格式：`[FILE: D:\full\path\to\file.md] (name=filename, size=1234)`
- 圖片格式：`[IMAGE: D:\full\path\to\image.jpg]`

```python
# ✅ 正確
abs_path = local_path.resolve()
payload = f"[FILE: {abs_path}] (name={filename}, size={size})"

# ❌ 錯誤：相對路徑在 agent CWD 中找不到
payload = f"[FILE: media/leader-agent/file.md]"
```

---

## 6. Telegram Bot Handler 規範

### Command vs Text
- Telegram 的 python-telegram-bot 框架將 `/` 開頭的訊息歸類為 `COMMAND`
- `filters.TEXT & ~filters.COMMAND` 會**排除**所有 `/` 開頭的訊息
- 必須同時註冊 `COMMAND` handler 來處理 `/help`、`/mode` 等指令

```python
# ✅ 正確：同時處理 TEXT 和 COMMAND
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text))
app.add_handler(MessageHandler(filters.COMMAND, self._on_command))

# ❌ 錯誤：只處理 TEXT，/help 等指令會被忽略
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text))
```

### @botname 後綴處理
- 群組中的指令可能帶有 `@botname` 後綴（如 `/help@rd7_test123_bot`）
- 必須在解析指令前移除 `@botname` 部分

---

## 7. 模型名稱規範

### 可用模型（以 kiro-cli 實際支援為準）
| 簡稱 | 完整名稱 | 用途 |
|------|---------|------|
| opus | claude-opus-4.6 | 預設，最強 |
| sonnet | claude-sonnet-4 | 快速平衡 |
| haiku | claude-haiku-4.5 | 最快，輕量 |

### 注意事項
- 模型名稱必須完全匹配 kiro-cli 支援的格式
- `claude-opus-4` ❌ → `claude-opus-4.6` ✅
- `claude-haiku-4` ❌ → `claude-haiku-4.5` ✅
- 如果不確定，使用 `kiro-cli chat --help` 查看可用模型

---

## 8. Port 管理與 uvicorn 啟動

### 問題
- uvicorn 如果 port 被佔用會呼叫 `sys.exit(1)`，導致整個程式崩潰
- 前一次的 process 如果沒有完全清理，port 會被佔用

### 規則
- 啟動前確認 port 未被佔用
- 停止 team 時必須確保所有子 process 都被終止
- 包含：kiro-cli process、uvicorn server、任何佔用 port 的 process

---

## 9. 即時回饋規範

### 問題
- 長任務（建立 agent、讀取大檔案）可能需要數分鐘
- 用戶在等待期間看不到任何回應，會以為系統當機

### 規則
- 收到檔案/圖片時，立即發送「🔄 收到檔案，處理中...」確認
- 超時時發送「⚠️ 處理超時，請稍後再試」
- 錯誤時發送「❌ 處理錯誤：{簡要說明}」
- 長任務中途使用 `report_progress()` 回報進度

---

## 10. team.yaml 配置規範

### 必填欄位
```yaml
instances:
  agent-name:
    working_directory: ./agents/agent-name  # 必填
    description: "繁體中文描述"              # 必填
    topic_id: <真實的 Telegram topic_id>    # 必填，不可用假值
    role: worker                            # 必填：worker 或 leader
```

### 禁止事項
- 不可使用假的 topic_id（如 3, 4 等隨意數字）
- 不可省略 working_directory
- description 必須使用繁體中文
