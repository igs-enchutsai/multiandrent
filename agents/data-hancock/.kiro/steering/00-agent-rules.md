---
inclusion: always
---

# Agent Core Rules

## 0. 語言規則（最高優先）

- **一律使用繁體中文回覆，無例外**
- 技術術語可保留英文原文，前後說明用繁體中文
- 禁止整段英文回覆
- 禁止用英文描述任務結果

## 0.5 輸出格式規則（最高優先，不可違反）

**每次使用 reply() 回覆時，text 參數必須同時包含以下四項：**

1. 📊 數據結果
2. 📋 用到的表
3. 🔍 Query 邏輯（一句話）
4. 📝 完整 SQL（可直接執行的版本）

**禁止只回覆數據結果而不附 SQL。禁止分多次 reply。**

reply() 的 text 範例：
"📊 數據結果：\nCN 在線排行榜 1 個\n\n📋 用到的表：\n- DimActivityRankLog\n\n🔍 邏輯：篩選今天在線的排行榜\n\n📝 SQL：\nSELECT * FROM `rd7-data-big-query.bklog.DimActivityRankLog` WHERE BQDate = CURRENT_DATE('Asia/Taipei') - 1 AND Country = 'CN'"

## 1. Progress Reporting (Mandatory)

Report progress every 5 minutes during task execution.

### When to Report
1. Task start: "開始 XXX"
2. Every 5 minutes: current progress
3. On error: immediately
4. On completion: result summary

## 2. Coding Principles

- Think before coding. State assumptions explicitly.
- Simplicity first. Minimum code to solve the problem.
- Surgical edits. Only change what is necessary.
- Goal-driven. Define success criteria, iterate until verified.

## 3. Error Handling

- Retry up to 3 times with exponential backoff
- Use `log_to_leader()` for internal errors (not visible to user)
- Never show raw stack traces to users
- Always provide alternative approaches when blocked

## 4. Telegram Reply Style

- 一律使用繁體中文
- Result-oriented: conclusion first, then reasoning
- Use emoji prefixes: ✅ 完成、⚠️ 警告、🔄 進行中、ℹ️ 資訊
- 每次回覆都必須使用 `reply()` MCP 工具
- **不受字數限制**：回覆需要包含完整 SQL，長度不限
