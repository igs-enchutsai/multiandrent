# Data-Hancock Issues

## Issue: 回覆不附完整 SQL

**日期：** 2026-05-14
**症狀：** Agent 回覆用戶時只給數據結果摘要，不附上使用的 SQL query
**根因：** 可能原因：
1. steering 檔案太多/太大，kiro-cli context window 被佔滿，規則被截斷
2. Agent 傾向簡潔回覆（受 00-agent-rules 的 "Concise" 影響）
3. reply() 的 text 長度可能有隱性限制
**解法：**
- 已將輸出格式規則放到 00-agent-rules.md 最前面（Section 0.5）
- 已將大型參考檔改為 manual inclusion
- 已移除 300 字限制
- 已給出 reply() 的實際 text 參數範例
**狀態：** 🔄 觀察中 — 需要進一步測試確認是否生效
