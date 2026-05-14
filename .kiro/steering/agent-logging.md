---
inclusion: always
---

# Agent 優化與執行紀錄規範

## 目的

所有 Agent 的優化歷程和重要執行紀錄都必須寫回專案目錄，確保未來可以從 Kiro IDE 進行：
- 回顧每個 Agent 的演進過程
- 追蹤 steering 規則的修改原因
- 整理常見問題和解法
- 持續優化 Agent 行為

## 紀錄結構

每個 Agent 目錄下維護一個 `logs/` 資料夾：

```
agents/{agent-name}/
├── logs/
│   ├── changelog.md        # steering/設定的修改紀錄
│   ├── issues.md           # 遇到的問題與解法
│   └── insights.md         # 執行中發現的洞察與優化建議
```

## changelog.md 格式

記錄每次對 Agent 的 steering、MCP 設定、角色定義的修改：

```markdown
## YYYY-MM-DD 修改摘要

**修改檔案：** steering/xxx.md
**原因：** [為什麼要改]
**改動：** [改了什麼]
**效果：** [改完後的觀察結果]
```

## issues.md 格式

記錄 Agent 執行中遇到的問題：

```markdown
## Issue: [問題標題]

**日期：** YYYY-MM-DD
**症狀：** [Agent 做了什麼不對的事]
**根因：** [為什麼會這樣]
**解法：** [怎麼修的]
**狀態：** ✅ 已解決 / 🔄 觀察中
```

## insights.md 格式

記錄執行中發現的優化機會：

```markdown
## Insight: [洞察標題]

**日期：** YYYY-MM-DD
**觀察：** [發現了什麼]
**建議：** [可以怎麼改善]
**優先級：** 高 / 中 / 低
```

## 規則

1. **每次修改 Agent 的 steering 或設定時，必須同步更新 changelog.md**
2. **Agent 行為不符預期時，記錄到 issues.md**
3. **發現可優化的地方時，記錄到 insights.md**
4. **這些紀錄檔案必須 commit 到 git**，確保團隊可追蹤
5. **從 Kiro IDE 優化 Agent 時，先讀 logs/ 了解歷史再動手**
