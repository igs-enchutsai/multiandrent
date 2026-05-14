# Data-Hancock Insights

## Insight: Steering 規則遵守度與 context window 的關係

**日期：** 2026-05-14
**觀察：** 當 steering 檔案總量過大時（bq-table-schemas.md ~7000 行 + query-warehouse-final.md ~345 行），Agent 可能無法完整讀取所有規則，導致行為規範被忽略
**建議：**
1. 關鍵行為規則放在 00-agent-rules.md 最前面
2. 大型參考資料改用 manual inclusion 或拆分成更小的檔案
3. 考慮把 schema 資訊做成 MCP tool（按需查詢）而非全部塞進 steering
**優先級：** 高

## Insight: pipe syntax 偏好

**日期：** 2026-05-14
**觀察：** 用戶的 Query Warehouse 中大量使用 BigQuery pipe syntax（`|>`），這是較新的語法
**建議：** data-hancock 生成 SQL 時應優先使用 pipe syntax，與用戶習慣一致
**優先級：** 中
