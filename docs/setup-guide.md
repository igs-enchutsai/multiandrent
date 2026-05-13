# Kiro Multi-Agent 完整設定指南

## 經驗總結

本次從零開始完成了以下工作：
1. 安裝 Python 套件與 Kiro CLI
2. 建立 Telegram Bot 連線（取得 group_id、topic_id、user_id）
3. 實作 TelegramAdapter（訊息路由、長文字分割、圖片/檔案收發）
4. 整合 kiro-cli subprocess 作為 agent 大腦
5. 建立 HoYeah API MCP Server（營運數據查詢）
6. 解決一系列 stdout 解析、timing、過濾問題

### 踩過的坑

| 問題 | 原因 | 解法 |
|------|------|------|
| kiro-cli model 不存在 | team.yaml 用了舊 model 名稱 | 用 `kiro-cli chat --list-models` 確認可用 model |
| stdout 讀不到輸出 | kiro-cli 用 `\r` 更新畫面，`readline()` 等不到 `\n` | 改用 `read(4096)` chunk-based 讀取 |
| 回覆有 ANSI 亂碼 | 終端機控制碼和 spinner 動畫 | 用 regex 過濾 ANSI escape + braille spinner |
| 新訊息被阻塞 | handler 用 `await` 等回覆，阻塞整個 event loop | 改用 `asyncio.create_task` 非阻塞處理 |
| MCP server 被覆蓋 | `write_config` 每次覆寫整個 mcp.json | 改為 merge 模式，只更新 team server |
| 回覆是 tool 參數 JSON | idle_timeout 太短，tool 執行中就截斷了 | 改為監聽 `▸ Time:` 結束標記 |
| API 回覆不完整 | model 用 `default` 而非 `hermes-agent` | 參考既有專案修正 model 名稱 |

---

## 一鍵設定提詞（給後續使用者）

將以下提詞貼入 Kiro IDE 的對話框，即可引導 AI 完成完整設定：

---

```
請幫我完成 Kiro Multi-Agent 的完整初始化與啟動，按照以下步驟執行：

## 1. 環境安裝
- 執行 `pip install -e ".[dev]"` 安裝所有依賴
- 確認 Python >= 3.11
- 確認 kiro-cli 已安裝（路徑通常在 `%LOCALAPPDATA%\Programs\Kiro-Cli\LocalApp\Kiro-Cli\kiro-cli.exe`）
- 執行 `kiro-cli whoami` 確認已登入
- 執行 `kiro-cli chat --list-models` 確認可用 model 列表

## 2. Telegram Bot 設定
- 讀取 .env 中的 TELEGRAM_BOT_TOKEN
- 執行 scripts/get_ids.py 監聽訊息
- 我會在 Telegram 群組的各個 Forum Topic 發訊息
- 取得 group_id、各 topic_id、我的 user_id
- 用 Bot API 建立需要的 Forum Topic（需要 bot 有管理員 + 管理話題權限）

## 3. team.yaml 設定
- 填入 group_id、allowed_users
- 確認 defaults.model 在 kiro-cli 可用 model 列表中
- 為每個 agent 設定正確的 topic_id 和 working_directory

## 4. Agent 目錄建立
- 從 templates/agent-template/ 複製到 agents/{name}/
- 修改 .kiro/settings/mcp.json（替換 instance name、role）
- 加入 language.md steering（指定繁體中文回覆）
- 加入該 agent 專屬的 steering 檔案

## 5. 啟動與驗證
- 執行 `python -m kiro_multi_agent team start`
- 確認 API status 顯示所有 instance 為 running
- 在 Telegram 發訊息測試回覆
- 確認回覆乾淨（無 ANSI 亂碼、無 JSON tool 參數）

## 重要注意事項
- kiro-cli 的 stdout 需要用 chunk-based read（不能用 readline）
- 回覆結束的標記是 `▸ Time:`，用這個判斷回覆完成
- MCP config 要用 merge 模式，不能覆蓋已有的 server
- Telegram handler 必須用 asyncio.create_task 非阻塞處理
- HoYeah API 的 model 參數要用 "hermes-agent"，timeout 要 600 秒
- 所有 agent 的 steering 都要加 language.md 指定繁體中文

## 我的環境資訊
- OS: Windows
- Telegram Bot Token: 在 .env 中
- 群組已開啟 Forum Topics
- Bot 已有管理員權限（含管理話題）
```

---

## 快速啟動命令

```bash
# 安裝
pip install -e ".[dev]"

# 確認 kiro-cli
kiro-cli whoami
kiro-cli chat --list-models

# 啟動
python -m kiro_multi_agent team start

# 停止
python -m kiro_multi_agent team stop
# 或直接 Ctrl+C
```

## 新增 Agent 流程

1. 複製 template：
```bash
cp -r templates/agent-template agents/{new-agent-name}
```

2. 修改 `agents/{name}/.kiro/settings/mcp.json`：
   - 替換 `__AGENT_NAME__` 為 agent 名稱
   - 替換 `role` 為 worker 或 leader
   - 如需額外 MCP server（如 hoyeah），加入對應設定

3. 加入 steering 檔案：
   - `language.md` — 指定回覆語言
   - 專屬 steering — 定義 agent 行為和能力

4. 在 Telegram 建立 Forum Topic（可用 Bot API）

5. 更新 `team.yaml` 加入新 instance

6. 重啟 team

## 檔案結構

```
kiro-multi-agent/
├── .env                          # Telegram Bot Token
├── team.yaml                     # 團隊設定（group_id, instances）
├── src/kiro_multi_agent/
│   ├── telegram_adapter.py       # Telegram 訊息路由
│   ├── daemon.py                 # Instance 生命週期管理
│   ├── process.py                # kiro-cli subprocess 管理
│   ├── backend.py                # kiro-cli 命令建構
│   ├── api.py                    # FastAPI REST API
│   ├── hoyeah_mcp.py            # HoYeah API MCP Server
│   ├── team_mcp.py              # 跨 Agent 通訊 MCP
│   ├── team.py                   # TeamManager 主流程
│   ├── config.py                 # team.yaml 載入
│   └── cli.py                    # CLI 入口
├── agents/
│   ├── leader-agent/             # Leader agent
│   │   └── .kiro/steering/       # 行為規則
│   └── hoyeah-api/               # 營運數據查詢 agent
│       └── .kiro/steering/       # 行為規則 + API 使用指南
└── scripts/
    ├── get_ids.py                # 取得 Telegram IDs 工具
    └── watchdog.py               # 程序監控（生產環境）
```
