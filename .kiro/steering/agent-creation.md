---
inclusion: always
---

# Agent 建立準則

## 必須從 Template 複製

建立新 agent 時，**必須**從 `templates/agent-template/` 複製完整結構，然後再修改。

## 強制規範

1. **每個 Agent 必須有獨立的 Telegram Forum Topic** — 不可省略、不可共用
2. **所有回覆必須使用繁體中文** — 包含建立過程中的所有訊息
3. **沒有 topic_id 不可完成建立** — 必須先建立 Topic 取得 ID

### 步驟
1. 複製 `templates/agent-template/` 到 `agents/{new-agent-name}/`
2. 修改 `.kiro/settings/mcp.json`：
   - 替換 `__AGENT_NAME__` 為 agent 名稱
   - 替換 `role` 為 worker 或 leader
   - 如需額外 MCP server，加入對應設定
3. 保留所有 template steering 檔案（不可刪除）：
   - `00-agent-rules.md` — 核心行為規則
   - `error-recovery.md` — 錯誤處理 SOP
   - `local-llm.md` — kiro-cli 與 MCP 通訊規範
   - `media-handling.md` — 媒體處理規範
   - `tech-stack.md` — 技術選型指南
   - `test-policy.md` — 測試與驗證規範
4. 加入 `language.md` — 指定繁體中文回覆（強制）
5. 加入該 agent 專屬的 steering 檔案（如 `project.md`）
6. **使用 `create_forum_topic(name, instance)` 建立獨立 Topic**
   - 工具會自動建立 Topic 並回傳 topic_id
   - 工具會自動建立 routing mapping
7. 更新 `team.yaml` 加入新 instance（必須包含 topic_id）
8. **使用 `restart_team()` 重啟所有 Agent**（自動載入新配置）

### team.yaml instance 格式（必須包含 topic_id）
```yaml
  agent-name:
    working_directory: ./agents/agent-name
    description: "Agent 描述（繁體中文）"
    topic_id: <create_forum_topic 回傳的 topic_id>
    role: worker
```

### 禁止事項
- ❌ 不可跳過 template 直接手動建立 agent 目錄
- ❌ 不可刪除 template 中的任何 steering 檔案
- ❌ 不可省略 `error-recovery.md`（所有 agent 都需要錯誤處理能力）
- ❌ 不可省略 topic_id（每個 Agent 必須有獨立 Topic）
- ❌ 不可讓多個 Agent 共用同一個 Topic
- ❌ 不可在沒有 topic_id 的情況下完成 Agent 建立流程
- ❌ 不可用英文回覆
- ❌ 不可使用假的 topic_id（必須是 create_forum_topic 回傳的真實值）

### Template 包含的基礎能力
| 檔案 | 提供的能力 |
|------|-----------|
| 00-agent-rules.md | 進度回報、程式原則、錯誤處理、Telegram 回覆風格 |
| error-recovery.md | L1/L2/L3 錯誤分級、重試策略 |
| local-llm.md | kiro-cli stdin/stdout 規範、MCP tool 使用、模型規範 |
| media-handling.md | 圖片/檔案接收與發送、絕對路徑規則 |
| tech-stack.md | Go/Python 技術選型、Port 管理、防毒規則 |
| test-policy.md | 修改後驗證步驟、常見陷阱 |
