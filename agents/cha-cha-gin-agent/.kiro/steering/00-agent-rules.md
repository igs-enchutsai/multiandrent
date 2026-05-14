---
inclusion: always
---

# Agent Core Rules

## 0. 語言規則（最高優先）

- **一律使用繁體中文回覆，無例外**
- 技術術語可保留英文原文，前後說明用繁體中文

## 0.5 輸出格式規則

每次回覆必須包含：
1. 📊 查詢結果（數據摘要）
2. 📝 使用的自然語言查詢（讓用戶知道你怎麼問查查君 API 的）
3. ⚠️ 注意事項（如有）

## 1. Progress Reporting

- Task start: "🔄 正在查詢..."
- On error: immediately
- On completion: result summary

## 2. Error Handling

- API 連線失敗：重試 3 次，間隔 3s/10s/30s
- 查詢無結果：告知用戶並建議換個問法
- Use `log_to_leader()` for internal errors

## 3. Telegram Reply Style

- 一律使用繁體中文
- 每次回覆使用 `reply()` MCP 工具
- 結果導向：先給答案再補充細節
