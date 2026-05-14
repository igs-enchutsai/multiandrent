---
inclusion: always
---

# BigQuery Pipe Syntax 風格指南

## 核心原則

使用 pipe syntax（`|>`）撰寫 SQL，每個 pipe operator 執行一個邏輯步驟，從上到下閱讀即為資料流方向。

## 常用 Pipe Operators

| Operator | 用途 | 範例 |
|----------|------|------|
| `|> where` | 篩選 | `|> where BQDate = '2026-05-01'` |
| `|> select` | 選取欄位 | `|> select UserID, BQDate` |
| `|> extend` | 新增計算欄位 | `|> extend TotalBet / TotalBetTimes as AvgBet` |
| `|> aggregate ... group by` | 聚合 | `|> aggregate sum(Revenue) as total group by BQDate` |
| `|> order by` | 排序 | `|> order by BQDate desc` |
| `|> limit` | 限制行數 | `|> limit 100` |
| `|> left join` | 左連接 | `|> left join table2 on key = key2` |
| `|> set` | 修改欄位值 | `|> set Status = if(Amount > 0, 'paid', 'free')` |

## 撰寫風格

```sql
# 好的 pipe syntax 範例：每日各服營收
from `rd7-data-big-query.bklog.GameConsume`
|> where BQDate between '2026-05-01' and '2026-05-07'
    and Country = 'CN'
|> aggregate
    sum(BuyNumber) as revenue,
    count(distinct UserID) as paying_users,
    count(distinct OrderID) as order_count
    group by BQDate
|> order by BQDate desc
```

```sql
# 加入維度表的範例
from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
|> where BQDate = current_date('Asia/Taipei') - interval 1 day
    and Country = 'CN'
|> aggregate
    sum(TotalBet) as total_bet,
    sum(TotalWin) as total_win,
    count(distinct UserID) as player_count
    group by TableTypeID
|> left join (
    select TableTypeID, TableTypeName
    from `rd7-data-big-query.bklog.DimTableTypeID`
  ) using (TableTypeID)
|> extend total_win / total_bet as rtp
|> order by total_bet desc
```

```sql
# 使用 CTE + pipe 的混合模式（複雜查詢）
with user_tags as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate = date_trunc(current_date('Asia/Taipei'), month)
  |> select UserID, NewUserTag
)

from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
|> where BQDate = current_date('Asia/Taipei') - interval 1 day
|> left join user_tags using (UserID)
|> aggregate
    count(distinct UserID) as dau,
    sum(BuyNumber) as revenue
    group by NewUserTag
|> order by revenue desc
```

## 規則

1. **FROM 放最前面**（不是 SELECT）
2. **每個 `|>` 獨立一行**，縮排對齊
3. **複雜條件換行縮排**（and/or 開頭）
4. **註解用 `#` 而非 `--`**（pipe syntax 慣例）
5. **CTE 用 `with` 搭配 pipe**（CTE 內部也用 pipe）
