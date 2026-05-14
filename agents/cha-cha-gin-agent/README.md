# 查查君 Agent (Cha-Cha-Gin)

透過自然語言查詢遊戲營運數據的助手，後端為查查君 Text2SQL API。

## 功能
- 自然語言 → SQL → 數據結果
- 支援多種快捷指令（/revenue, /dau, /bp, /rank, /user, /trend）
- 可作為其他 Agent 的數據查詢服務

## API
- Endpoint: `http://18.140.142.14:8080/text2sql/text2sql`
- Method: POST
- Input: `{"question": "自然語言問題", "execute": true}`

## 指令
- `/help` — 完整指令說明
- `/revenue` — 營收查詢
- `/dau` — 活躍用戶查詢
- `/bp` — Battle Pass 查詢
- `/rank` — 排行榜查詢
- `/user [id]` — 玩家查詢
- `/trend [metric]` — 趨勢查詢
- `/sql [query]` — 直接執行 SQL
