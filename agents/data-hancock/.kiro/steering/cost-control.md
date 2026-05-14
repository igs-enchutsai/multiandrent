---
inclusion: always
---

# BigQuery 成本控制規則

## 掃描量估算

| 表 | 每日約行數 | 每日約大小 |
|----|-----------|-----------|
| SessionTigerSharkBetWinLog | ~5M rows/day | ~2 GB/day |
| SessionActive | ~1.5M rows/day | ~500 MB/day |
| DailyUserInfoSnapshot | ~250K rows/day | ~1 GB/day |
| ActivityMissionCompleteLog | ~3M rows/day | ~800 MB/day |
| SessionItemLog | ~9M rows/day | ~3 GB/day |
| GameConsume | ~40K rows/day | ~50 MB/day |

## 成本規則（強制）

### 必須遵守
1. **所有查詢必須有 BQDate 分區條件**（除非表沒有 BQDate）
2. **避免 SELECT ***：只選需要的欄位
3. **單次查詢掃描不超過 100 GB**
4. **如果需要大範圍查詢（> 30 天），先用 COUNT(*) 估算行數**

### 危險操作（需要確認）
- 查詢 SessionItemLog 超過 7 天 → 預估掃描 > 20 GB
- 查詢 SessionTigerSharkBetWinLog 超過 14 天 → 預估掃描 > 30 GB
- 任何 CROSS JOIN → 可能產生笛卡爾積
- 沒有 WHERE 條件的大表查詢

### 優化技巧
1. **先聚合再 JOIN**（減少 JOIN 的行數）
2. **用 EXISTS 代替 IN**（大列表時更快）
3. **用 APPROX_COUNT_DISTINCT 代替 COUNT(DISTINCT)**（允許誤差時）
4. **分段查詢**：如果需要 90 天資料，分成 3 個 30 天查詢再 UNION

## 查詢前 Checklist

每次生成 SQL 前確認：
- [ ] 有 BQDate 分區條件？
- [ ] 時間範圍合理？（不超過必要）
- [ ] 只選了需要的欄位？
- [ ] 有 LIMIT 或 GROUP BY？（避免輸出百萬行）
- [ ] JOIN 的 key 是否正確？（避免笛卡爾積）
