# Data-Hancock Changelog

## 2026-05-14 建立 Agent + 知識庫

**修改檔案：** 全部（新建）
**原因：** 建立活動分析團隊的 BQ 資料工程師 Agent
**改動：**
- 建立 steering: 00-agent-rules.md, data-engineer-role.md, error-recovery.md, local-llm.md, media-handling.md, tech-stack.md
- 建立知識庫: notion-bq-notes.md, bq-table-schemas.md, query-warehouse-final.md
- 設定 MCP: team server (worker role)
**效果：** Agent 成功啟動，能回答 BQ 相關問題

## 2026-05-14 輸出格式規範（多次迭代）

**修改檔案：** 00-agent-rules.md, output-format.md (已刪除), data-engineer-role.md
**原因：** Agent 回覆時只給數據結果，不附 SQL query
**改動：**
1. 第一次：新增 output-format.md 獨立檔案 → 無效
2. 第二次：加強 output-format.md 規則 + 給 reply() 範例 → 無效
3. 第三次：把規則合併到 00-agent-rules.md Section 0.5（最先載入）+ 大型參考檔改 manual inclusion → 觀察中
**效果：** 🔄 觀察中 — Agent 仍未完全遵守，可能是 kiro-cli context window 限制
