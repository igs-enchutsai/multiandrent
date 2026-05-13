# 🚀 Kiro Multi-Agent 初始設定指南

本指南會引導你從零開始設定整個 Multi-Agent 環境。
請按照順序執行每個步驟。

---

## 步驟 1：安裝環境

### 1.1 確認必要軟體

```bash
python --version    # 需要 >= 3.11
go version          # 需要 >= 1.22
git --version
```

### 1.2 確認 Kiro CLI 已安裝

```bash
kiro-cli whoami
```

如果未登入，執行：
```bash
kiro-cli login --license free
```
會開啟瀏覽器進行網頁認證。

### 1.3 確認可用模型

```bash
kiro-cli chat --help
```
確認 `claude-opus-4.6` 在可用模型列表中。

### 1.4 安裝 Python 依賴

```bash
pip install -e ".[dev]"
```

---

## 步驟 2：建立 Telegram Bot

### 2.1 建立 Bot

1. 在 Telegram 搜尋 `@BotFather`
2. 發送 `/newbot`
3. 輸入 Bot 名稱（例如：`我的 Multi-Agent Bot`）
4. 輸入 Bot username（例如：`my_multi_agent_bot`）
5. **記下 Bot Token**（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2.2 建立 Telegram Group

1. 在 Telegram 建立一個新群組
2. 開啟群組設定 → **開啟 Topics（論壇模式）**
3. 把你的 Bot 加入群組
4. 設定 Bot 為**管理員**，勾選以下權限：
   - ✅ 管理話題（Manage Topics）
   - ✅ 發送訊息
   - ✅ 刪除訊息

### 2.3 建立 Forum Topics

在群組中建立以下 Topic：
- **Leader** — leader-agent 的對話入口

（其他 agent 的 Topic 可以之後由 leader-agent 自動建立）

---

## 步驟 3：設定 .env

### 3.1 複製範本

```bash
cp .env.example .env
```

### 3.2 填入 Bot Token

編輯 `.env`，把 `your_bot_token_here` 替換為步驟 2.1 取得的 Token：

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## 步驟 4：取得 Telegram ID

### 4.1 執行 ID 監聽工具

```bash
python scripts/get_ids.py
```

### 4.2 在 Telegram 發訊息

在你建立的群組的 **Leader Topic** 中發送任意訊息。
終端會印出：

```
==================================================
  Chat ID (group_id):    -100xxxxxxxxxx
  Topic ID (thread_id):  2
  User ID:               123456789
==================================================
```

### 4.3 記下以下資訊

| 資訊 | 用途 | 範例 |
|------|------|------|
| Chat ID | group_id | -1001234567890 |
| Leader Topic 的 thread_id | leader topic_id | 2 |
| 你的 User ID | allowed_users | 123456789 |

按 `Ctrl+C` 停止監聽。

---

## 步驟 5：設定 team.yaml

編輯根目錄的 `team.yaml`：

```yaml
# Kiro Multi-Agent Team Configuration

channel:
  bot_token_env: TELEGRAM_BOT_TOKEN
  group_id: <填入你的 Chat ID>
  general_topic_id: 1

access:
  mode: locked
  allowed_users: [<填入你的 User ID>]

defaults:
  backend: kiro-cli
  model: claude-opus-4.6

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
    description: "團隊領導 - 任務協調與分派"
    topic_id: <填入 Leader Topic 的 thread_id>
    role: leader
    general_topic: true

health_port: 8470
```

---

## 步驟 6：啟動服務

```bash
python -m kiro_multi_agent team start
```

### 確認啟動成功

你應該看到：
```
INFO  Team ready: 1/1 running
INFO  Telegram bot started polling
INFO  API started on port 8470
```

### 測試

在 Telegram 的 Leader Topic 發送 `/help`，應該收到指令說明。

---

## 步驟 7：驗證完整功能

| 測試 | 操作 | 預期結果 |
|------|------|---------|
| 文字對話 | 在 Leader Topic 發「你好」 | 收到繁體中文回覆 |
| 指令 | 發 `/help` | 收到可用指令列表 |
| 模型切換 | 發 `/mode sonnet` | 收到切換確認 |
| 檔案上傳 | 上傳一個 .md 檔案 | 收到「🔄 收到檔案，處理中...」 |

---

## 常見問題

| 問題 | 解法 |
|------|------|
| `Bot token not found` | 確認 .env 中 TELEGRAM_BOT_TOKEN 已填入 |
| `Model does not exist` | 用 `kiro-cli chat --help` 確認模型名稱 |
| Port 8470 被佔用 | 關閉佔用的程式或改 team.yaml 的 health_port |
| Bot 沒有回應 | 確認 Bot 是群組管理員且有「管理話題」權限 |
| `/help` 沒反應 | 確認 topic_id 正確（用 get_ids.py 重新確認） |
| kiro-cli 未登入 | 執行 `kiro-cli login --license free` |

---

## 下一步

設定完成後，你可以：
1. 在 Leader Topic 指揮 leader-agent 建立新的 Agent
2. 上傳需求文件讓 leader-agent 自動建立對應的 Agent
3. 使用 `/mode` 切換不同的 AI 模型

所有新 Agent 都會自動建立獨立的 Forum Topic 並加入 team。
