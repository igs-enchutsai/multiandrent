---
inclusion: always
---

# Agent Core Rules

## 0. 語言規則（最高優先）

- **一律使用繁體中文回覆，無例外**
- 技術術語可保留英文原文，前後說明用繁體中文

## 1. Progress Reporting

Report progress every 5 minutes during task execution.

## 2. Error Handling

- Retry up to 3 times with exponential backoff
- Use `log_to_leader()` for internal errors
- Always provide alternative approaches when blocked

## 3. Telegram Reply Style

- 一律使用繁體中文
- 每次回覆使用 `reply()` MCP 工具
- 結果導向：先給結論再補充分析
- Use emoji prefixes: ✅ 完成、⚠️ 警告、🔄 進行中
