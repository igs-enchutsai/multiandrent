# Event-King Changelog

## 2026-05-15 補齊 template 檔案 + 功能擴充

**修改檔案：** 00-agent-rules.md, intent-classification.md, test-policy.md（新增）
**原因：** 
1. 缺少 template 的 test-policy.md
2. Leader 不應有 300 字限制（整合多 Agent 結果需要較長回覆）
3. 新增 cha-cha-gin-agent 和 boss-predictor-agent 的分派邏輯
**改動：**
- 補上 test-policy.md
- 移除 300 字限制，改為「Leader 不受字數限制」
- intent-classification.md 加入查查君（簡單查詢）和 Boss Predictor（規格/偏好）的分派路徑
- 區分簡單查詢（→ cha-cha-gin）vs 複雜查詢（→ data-hancock）
**效果：** 待觀察

**修改檔案：** collaboration-sop.md, intent-classification.md（新增）
**原因：** 強化任務分派精確度和多 Agent 協作效率
**改動：**
- `collaboration-sop.md`：串行/並行協作模式、分派訊息格式、回覆整合原則
- `intent-classification.md`：用戶意圖分類決策樹、模糊情境判斷表、追問處理規則
**效果：** 待觀察

## 2026-05-14 建立 Agent

**修改檔案：** 全部（新建）
**原因：** 建立活動分析團隊的 Leader Agent
**改動：** 建立 steering + MCP 設定
**效果：** Agent 成功啟動
