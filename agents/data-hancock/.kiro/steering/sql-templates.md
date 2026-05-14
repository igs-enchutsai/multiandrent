---
inclusion: always
---

# 常用 SQL 模板（高頻查詢快速參考）

## 1. 每日營收

```sql
from `rd7-data-big-query.bklog.GameConsume`
|> where BQDate between @start_date and @end_date
    and Country = 'CN'
|> aggregate
    sum(BuyNumber) as revenue,
    count(distinct UserID) as paying_users,
    count(distinct OrderID) as orders
    group by BQDate
|> order by BQDate desc
```

## 2. DAU（每日活躍用戶）

```sql
from `rd7-data-big-query.bklog.SessionActive`
|> where BQDate between @start_date and @end_date
    and Country = 'CN'
|> aggregate count(distinct UserID) as dau group by BQDate
|> order by BQDate desc
```

## 3. BP 活動購買狀況

```sql
from `rd7-data-big-query.bklog.BattlePassBuyLog`
|> where BQDate between @start_date and @end_date
    and Country = 'CN'
|> aggregate
    sum(BuyNumber) as revenue,
    count(distinct UserID) as buyers,
    count(distinct OrderID) as orders
    group by BattlePassID
|> order by revenue desc
```

## 4. 排行榜在線狀況

```sql
from `rd7-data-big-query.bklog.DimActivityRankLog`
|> where BQDate = current_date('Asia/Taipei') - interval 1 day
    and Country = 'CN'
    and CountryOperation = 'and'
|> extend
    DATE(TIMESTAMP_SECONDS(StartEventTime), 'Asia/Taipei') as start_date,
    DATE(TIMESTAMP_SECONDS(EndEventTime), 'Asia/Taipei') as end_date
|> where start_date <= current_date('Asia/Taipei')
    and end_date >= current_date('Asia/Taipei')
|> select EventID, RankType, GameID, start_date, end_date, BetThreshold
```

## 5. 用戶分群統計

```sql
with user_tags as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate = date_trunc(current_date('Asia/Taipei'), month)
  |> select UserID, NewUserTag
)

from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
|> where BQDate = current_date('Asia/Taipei') - interval 1 day
|> left join user_tags using (UserID)
|> aggregate
    count(distinct UserID) as users,
    sum(BuyNumber) as revenue,
    sum(CoinBet) as total_bet
    group by NewUserTag
|> order by revenue desc
```

## 6. 活動任務完成率

```sql
from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
|> where BQDate between @start_date and @end_date
    and BatchID = @batch_id
|> aggregate
    max(MissionPriority) + 1 as max_level
    group by UserID
|> aggregate
    count(*) as user_count
    group by max_level
|> order by max_level
```

## 7. 員工帳號排除

```sql
# 排除員工帳號的標準寫法
and UserID not in (
  select distinct UserID
  from `rd7-data-big-query.bklog.GameAccount`
)
```

## 8. 風險帳戶標記

```sql
# 標記風險帳戶
|> left join (
    select distinct UserID, 1 as is_risk
    from `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
  ) using (UserID)
|> set is_risk = ifnull(is_risk, 0)
```
