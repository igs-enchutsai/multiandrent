---
inclusion: always
---

# Query Warehouse — 最終版本參考

以下為經確認的最終版本 SQL 範例，供撰寫新 query 時參考。

## [Analysis] 20251123 營收搶救BP
**描述：** 觀察某檔搶救疲弱大客BP活動績效

```sql
-- 目標: 觀察某檔搶救疲弱大客BP活動績效
-- batch_id: '2025-11-26#26e4c'
-- in_user_id:['107103359','107220327','58950363','41759839','52731355','34635874','25765660','66477369','51654772','28819822','30034877','44939896','34140813','48926066','106145501','44427542','107104408','48926066','105075679','53063145','104478817','32041011','28207016','52090229']


-- 有買目標BP的battlepassbuylog
select *
from `rd7-data-big-query.bklog.BattlePassBuyLog`
where BQDate >= '2025-11-26' and
      BattlePassID = concat('bp_', 
                            (select distinct EventName
                            from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
                            where BQDate >= '2025-11-26' and BatchID = '2025-11-26#26e4c')
                            );


-- 目標大客在目標BP活動的任務完成率
select UserID, Max(MissionPriority) + 1 as max_completelevel
from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
where BQDate >= '2025-11-26' and 
      BatchID = '2025-11-26#26e4c'
group by UserID;

-- 搶救活動的獎勵領取狀況
select UserID, MAX(MissionPriority) + 1 as reward_maxlevel
from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
where BQDate >= '2025-11-26' and
      BatchID = '2025-11-26#26e4c'
group by 1;


-- 目標大客的活躍天數
select UserID, COUNT( distinct LoginDate) as login_days
from `rd7-data-big-query.bklog.SessionActive`
where BQDate >= '2025-11-26' and
      UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229)
group by 1;


-- 目標大客在魚機的遊玩情況
select UserID, TableTypeID, SUM(TotalBet) as total_bet, SUM(TotalBetTimes) as total_bet_counts, SUM(TotalWin) as total_win
from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
where BQDate >= '2025-11-26' and
      UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229)
group by 1, 2;


-- 目標大客是否因該檔活動而又活躍起來玩 (活動在11/26晚上上的，觀察目標大客在 11/25往前四天 以及 11/27往後四天 的遊玩情況)
select UserID, TableTypeID, SUM(TotalBet) as total_bet, SUM(TotalBetTimes) as total_bet_counts, SUM(TotalWin) as total_win, 'before' as timing
from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
where BQDate BETWEEN '2025-11-22' AND '2025-11-25' and
      UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229)
group by 1, 2

UNION ALL

select UserID, TableTypeID, SUM(TotalBet) as total_bet, SUM(TotalBetTimes) as total_bet_counts, SUM(TotalWin) as total_win, 'after' as timing
from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
where BQDate BETWEEN '2025-11-27' AND '2025-11-30' and
      UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229)
group by 1, 2
;


--  目標大客在上搶救活動前後四天的營收貢獻
select UserID, SUM(BuyNumber) + (SUM(TotalCoinReceived) - SUM(TotalCoinSent)) / 4000000 as contribution, 'before' as timing
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229) and
      BQDate BETWEEN '2025-11-22' AND '2025-11-25'
group by UserID

UNION ALL 

select UserID, SUM(BuyNumber) + (SUM(TotalCoinReceived) - SUM(TotalCoinSent)) / 4000000 as contribution, 'after' as timing 
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229) and
      BQDate BETWEEN '2025-11-27' AND '2025-11-30'
group by UserID;



-- 水位
select *
from (
  select *, row_number() over(partition by UserID order by BQDate DESC) as recent
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  where BQDate >= '2025-11-01' and 
        UserID in (107103359,107220327,58950363,41759839,52731355,34635874,25765660,66477369,51654772,28819822,30034877,44939896,34140813,48926066,106145501,44427542,107104408,48926066,105075679,53063145,104478817,32041011,28207016,52090229)
  )
where recent = 1
;
```

## [Analysis] 新人第一個月期末
**描述：** 十月十一月BP分析

```sql
DECLARE start_date DATE DEFAULT DATE('2025-10-01');
DECLARE end_date DATE DEFAULT DATE('2025-10-31');-- DATE_SUB(CURRENT_DATE('Asia/Taipei'), INTERVAL 1 DAY);

WITH battlepass_performance AS
  (
    SELECT 
      BattlePassID,
      SUBSTRING(BattlePassID, 4) AS EventName,
      'CN' AS Market,
      ROUND(SUM(BuyNumber),2) AS revenue,
      COUNT(DISTINCT OrderID) AS order_counts,
      COUNT(DISTINCT UserID) AS buyer_counts
    FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
    WHERE BQDate BETWEEN start_date AND end_date AND Country = 'CN'
    GROUP BY BattlePassID
    ORDER BY　revenue DESC
  ),
-- 以下為BP活動資訊
  temp_table AS
(
  SELECT 
    DISTINCT 
        InGameMissionBookMark,
        MissionBookMark,
        ActivityType,
        PagePriority,
        ActivityStartTime,
        ActivityEndTime,
        RunDay,
        GameType,
        MissionFeatureCHT,
        GameCategory,
        BattlePassBuyNumber,
        PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(EventName, r'_(\d{8})_')) as which_round,
        EventName,
        BatchID,
        BatchIDTs,
  FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
  WHERE BQDate BETWEEN start_date AND end_date AND CountryOperation = 'for' AND Country = 'CN'
), 
  partitioned_temp AS -- 標示出 eventname 重複的: 活動上錯後關掉馬上重上就會有同樣eventname的情況產生
( 
  SELECT *, ROW_NUMBER() OVER(PARTITION BY EventName ORDER BY BatchIDTs DESC) AS recent_rank
  FROM temp_table
),
  battlepass_info AS -- 消除同樣EventName但在不同時間上的並取最新的
(
  SELECT *,
    CASE 
      WHEN ActivityEndTime > end_date and ActivityStartTime < start_date THEN DATE_DIFF(end_date, start_date, DAY) + 1
      WHEN ActivityEndTime > end_date and ActivityStartTime >= start_date THEN DATE_DIFF(end_date, ActivityStartTime, DAY) + 1
      WHEN ActivityEndTime <= end_date and ActivityStartTime < start_date THEN DATE_DIFF(ActivityEndTime, start_date, DAY) + 1
      WHEN ActivityEndTime <= end_date and ActivityStartTime >= start_date THEN DATE_DIFF(ActivityEndTime, ActivityStartTime, DAY) + 1
    END AS ActivityDuration
  FROM partitioned_temp
  WHERE recent_rank = 1
),
  battlepass_InfoAndPerformance AS -- 每個EventName的績效和其屬於MissionBookMark的資訊
(
  SELECT *
  FROM battlepass_performance bp
  LEFT JOIN battlepass_info bi
    ON bp.EventName = bi.EventName
), FinalCalculations AS -- 為了計算 ActivityType 內活動們各自日均收入的平均，作為該 ActivityType 的 performance 指標
(
  SELECT 
        *,
      SUM(revenue) OVER(PARTITION BY BatchID) AS batch_totalrevenue, -- 因為不同次上的活動有機會會有同樣的MissionBookMark，故使用BatchID確保同一次活動
      SUM(order_counts) OVER (PARTITION BY BatchID) AS batch_totalordercounts,
      AVG(ActivityDuration) OVER (PARTITION BY BatchID) AS batch_duration,
      ROW_NUMBER() OVER(PARTITION BY BatchID ORDER BY which_round DESC) AS label -- 建議在 ROW_NUMBER() 中加入 ORDER BY 以確保 label = 1 的結果一致
  FROM battlepass_InfoAndPerformance
)


SELECT
    *,
    
    -- 每個活動的 日均收入：只有 label = 1 時才計算，否則為 NULL
    CASE 
        WHEN label = 1 THEN SAFE_DIVIDE(batch_totalrevenue, batch_duration)
        ELSE NULL
    END AS batch_dailyavg_revenue,
    
    -- 每個活動的 日均訂單數：只有 label = 1 時才計算，否則為 NULL
    CASE 
        WHEN label = 1 THEN SAFE_DIVIDE(batch_totalordercounts, batch_duration)
        ELSE NULL
    END AS batch_dailyavg_ordercounts
FROM
    FinalCalculations
```

## [Analysis] 新人第一個月期末
**描述：** 十月十一月BP主要收入來源的慶典BP風險分析

```sql
-- 目的: 找出三慶典的風險玩家特徵，未來若要出相似BP要怎麼避免套利玩家
-- 'AA_魚慶典_排除負貢獻_七日_CN_v23456', 'AA_獵慶典_七日_CN_v23456', 'AA_惡慶典_七日_CN_v23456'
-- ('2025-11-02#20f83', '2025-11-23#97d74'), '2025-11-02#59c76', '2025-11-02#47edf'

WITH
  --- 惡慶典起---
  devil_buyer_info AS (
  select  a.*,
          UserTag,
          case when c.UserID is null then 0 else 1 end as flag
  from(  
    SELECT  DISTINCT -- 找出購買慶典的玩家(不分哪一round)
            UserID,
            VipLV 
    FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
    WHERE BattlePassID IN (
      SELECT DISTINCT CONCAT('bp_', EventName) AS BattlePassID
      FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
      WHERE
      BQDate between '2025-11-01' and '2025-11-30'
      and BatchID = '2025-11-02#47edf'
    )
  ) as a 
  left join(
    select  UserID, 
            UserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate = '2025-11-01'
    ) as b
    on a.UserID=b.UserID
  left join(
    select distinct UserID
    from `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
    ) as c
    on a.UserID=c.UserID
  
  
  ), devil_buyer_metric AS (
    SELECT  UserID, 
            COUNT(*) AS premonth_activedays , 
            SUM(BuyNumber) AS premonth_total_buynumber, 
            SUM(TotalCoinSent) AS premonth_total_coinsent, 
            SUM(TotalCoinReceived) AS premonth_total_coinreceived, 
            SUM(CoinBet) AS premonth_total_bet, 
            SUM(CoinBetTimes) AS premonth_total_bet_times
    FROM `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
    WHERE BQDate BETWEEN '2025-10-01' AND '2025-10-31' 
          AND UserID IN (SELECT DISTINCT UserID FROM devil_buyer_info)
    GROUP BY UserID
  
  
  ), devil_buyer_platform  AS ( -- 慶典買家的平台給予: 用於後續計算遊戲活躍(玩家10月的total bet / 玩家10月的平台給予 = 玩家10月的遊玩活躍度)
    SELECT UserID, SUM(Free + ProductFree) AS free_coin
    FROM `rd7-data-big-query.preprocessed_bklog.UserGrossRetLog`
    WHERE BQDate BETWEEN '2025-10-01' AND '2025-10-31'
          AND UserID IN (SELECT DISTINCT UserID FROM devil_buyer_info)
    GROUP BY 1
  
  
  ), devil_missioncomplete AS (

    SELECT UserID, MAX(MissionPriority) + 1 AS max_complete_level -- 假設玩家買了second round BP，該玩家即便在first round有玩，仍會在second round達到最高門檻
    FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
    WHERE BQDate > '2025-11-01'
          AND BatchID = '2025-11-02#47edf'
          AND UserID IN (SELECT DISTINCT UserID FROM devil_buyer_info)
    GROUP BY 1


  ), devil_final AS (
    SELECT 'devil' AS MissionBookMark, *, premonth_total_bet / free_coin AS BetFreecoinRatio
    FROM devil_buyer_info
    LEFT JOIN devil_buyer_metric
      USING (UserID)
    LEFT JOIN devil_buyer_platform
      USING (UserID)
    LEFT JOIN devil_missioncomplete
      USING (UserID)
  --- 惡慶典末 ---
  
  
  --- 魚慶典始 ---
  ),    fish_buyer_info AS (
  select  a.*,
          UserTag,
          case when c.UserID is null then 0 else 1 end as flag
  from(  
    SELECT  DISTINCT 
            UserID,
            VipLV 
    FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
    WHERE BattlePassID IN (
      SELECT DISTINCT CONCAT('bp_', EventName) AS BattlePassID
      FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
      WHERE
      BQDate between '2025-11-01' and '2025-11-30'
      and BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74')
    )
  ) as a 
  left join(
    select  UserID, 
            UserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate = '2025-11-01'
    ) as b
    on a.UserID=b.UserID
  left join(
    select distinct UserID
    from `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
    ) as c
    on a.UserID=c.UserID
  
  
  ), fish_buyer_metric AS (
    SELECT  UserID, 
            COUNT(*) AS premonth_activedays , 
            SUM(BuyNumber) AS premonth_total_buynumber, 
            SUM(TotalCoinSent) AS premonth_total_coinsent, 
            SUM(TotalCoinReceived) AS premonth_total_coinreceived, 
            SUM(CoinBet) AS premonth_total_bet, 
            SUM(CoinBetTimes) AS premonth_total_bet_times
    FROM `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
    WHERE BQDate BETWEEN '2025-10-01' AND '2025-10-31' 
          AND UserID IN (SELECT DISTINCT UserID FROM fish_buyer_info)
    GROUP BY UserID
  
  
  ), fish_buyer_platform  AS (
    SELECT UserID, SUM(Free + ProductFree) AS free_coin
    FROM `rd7-data-big-query.preprocessed_bklog.UserGrossRetLog`
    WHERE BQDate BETWEEN '2025-10-01' AND '2025-10-31'
          AND UserID IN (SELECT DISTINCT UserID FROM fish_buyer_info)
    GROUP BY 1
  
  
  ), fish_missioncomplete AS (

    SELECT UserID, MAX(MissionPriority) + 1 AS max_complete_level
    FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
    WHERE BQDate > '2025-11-01'
          AND BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74')
          AND UserID IN (SELECT DISTINCT UserID FROM fish_buyer_info)
    GROUP BY 1


  ), fish_final AS (
    SELECT 'fish' AS MissionBookMark, *, premonth_total_bet / free_coin AS BetFreecoinRatio
    FROM fish_buyer_info
    LEFT JOIN fish_buyer_metric
      USING (UserID)
    LEFT JOIN fish_buyer_platform
      USING (UserID)
    LEFT JOIN fish_missioncomplete
      USING (UserID)
  --- 魚慶典末 ---
  
  
  --- 獵慶典始 ---  
  ),  hunt_buyer_info AS (
  select  a.*,
          UserTag,
          case when c.UserID is null then 0 else 1 end as flag
  from(  
    SELECT  DISTINCT 
            UserID,
            VipLV 
    FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
    WHERE BattlePassID IN (
      SELECT DISTINCT CONCAT('bp_', EventName) AS BattlePassID
      FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
      WHERE
      BQDate between '2025-11-01' and '2025-11-30'
      and BatchID = '2025-11-02#59c76'
    )
  ) as a 
  left join(
    select  UserID, 
            UserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate = '2025-11-01'
    ) as b
    on a.UserID=b.UserID
  left join(
    select distinct UserID
    from `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
    ) as c
    on a.UserID=c.UserID
  
  
  ), hunt_buyer_metric AS (
    SELECT  UserID, 
            COUNT(*) AS premonth_activedays , 
            SUM(BuyNumber) AS premonth_total_buynumber, 
            SUM(TotalCoinSent) AS premonth_total_coinsent, 
            SUM(TotalCoinReceived) AS premonth_total_coinreceived, 
            SUM(CoinBet) AS premonth_total_bet, 
            SUM(CoinBetTimes) AS premonth_total_bet_times
    FROM `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
    WHERE BQDate BETWEEN '2025-10-01' AND '2025-10-31' 
          AND UserID IN (SELECT DISTINCT UserID FROM hunt_buyer_info)
    GROUP BY UserID
  
  
  ), hunt_buyer_platform  AS (
    SELECT UserID, SUM(Free + ProductFree) AS free_coin
    FROM `rd7-data-big-query.preprocessed_bklog.UserGrossRetLog`
    WHERE BQDate BETWEEN '2025-10-01' AND '2025-10-31'
          AND UserID IN (SELECT DISTINCT UserID FROM hunt_buyer_info)
    GROUP BY 1
  
  
  ), hunt_missioncomplete AS (

    SELECT UserID, MAX(MissionPriority) + 1 AS max_complete_level
    FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
    WHERE BQDate > '2025-11-01'
          AND BatchID = '2025-11-02#59c76'
          AND UserID IN (SELECT DISTINCT UserID FROM hunt_buyer_info)
    GROUP BY 1


  ), hunt_final AS (
    SELECT 'hunt' AS MissionBookMark, *, premonth_total_bet / free_coin AS BetFreecoinRatio
    FROM hunt_buyer_info
    LEFT JOIN hunt_buyer_metric
      USING (UserID)
    LEFT JOIN hunt_buyer_platform
      USING (UserID)
    LEFT JOIN hunt_missioncomplete
      USING (UserID)
  )

SELECT * FROM devil_final
UNION ALL
SELECT * FROM fish_final
UNION ALL
SELECT * FROM hunt_final;







-- -- *****************************魚慶典分隔線 **************************************
-- -- 目標: 列出魚慶典付費玩家的活動完成狀況

-- WITH 
--   fish_info AS ( -- 找出魚慶典的所有 eventname (因為BattlePassBuyLog只有eventname)
--     SELECT DISTINCT EventName, CONCAT('bp_', EventName) AS BattlePassID
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE 
--       BQDate >= '2025-11-01'
--       and BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74')
--   ), fish_bp_buyerID AS ( -- 找出有購買魚慶典BP的玩家(魚慶典共有三檔 11/2 11/9 11/16 11/23 11/30)，列出有購買的玩家和買哪一檔
--         SELECT DISTINCT UserID, BattlePassID, 
--           CASE 
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--             ELSE DATE('2025-11-30')
--               END AS ActivityStartTime,
--           CONCAT(UserID, '_', CASE WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--                               ELSE DATE('2025-11-30') END) 
--           AS buyer_period -- buyerid與其購買的檔期，才能從completelog篩出購買該檔期玩家的行為
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE BattlePassID IN (SELECT BattlePassID FROM fish_info)
--         ORDER BY UserID DESC
--   ), fish_completeLog AS (-- 整理魚慶典活動Log，為了接下來能找出購買特定檔期玩家的missioncompletelog
--         SELECT *,
--                EXTRACT(DATETIME FROM TIMESTAMP_SECONDS(EventTime) AT TIME ZONE 'Asia/Taipei') AS completed_time, 
--                datetime(TIMESTAMP_SECONDS(EventTime), 'UTC+8'),
--                EXTRACT(DATE FROM TIMESTAMP_SECONDS(StartTime) AT TIME ZONE 'Asia/Taipei') AS ActivityStartTime, 
--                CONCAT(UserID,'_', EXTRACT(DATE FROM TIMESTAMP_SECONDS(StartTime) AT TIME ZONE 'Asia/Taipei')) AS user_period 
--         FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
--         WHERE BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74')
--   ), fish_buyer_completeLog AS (-- 篩選出有購買BP玩家的任務完成資訊。因魚慶典有三檔，只選出玩家買BP該檔的紀錄，若買第二檔那就只篩出第二檔的資料
--         SELECT UserID, VipLV, completed_time, ActivityStartTime, MissionID, (MissionPriority + 1) AS MissionPriority 
--         FROM fish_completeLog
--         WHERE user_period IN (SELECT buyer_period FROM fish_bp_buyerID)
--         ORDER BY UserID DESC, ActivityStartTime DESC, MissionPriority DESC
--   ), fish_buyer_1_list AS ( -- 列出購買兩檔魚慶典的人
--         SELECT UserID
--         FROM fish_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 1
--   ), fish_buyer_2_list AS ( -- 列出購買兩檔魚慶典的人
--         SELECT UserID
--         FROM fish_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 2
--   ), fish_buyer_3_list AS ( -- 列出購買三檔魚慶典的人
--         SELECT UserID
--         FROM fish_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 3
--   ), fish_buyer_4_list AS ( -- 列出購買四檔魚慶典的人
--         SELECT UserID
--         FROM fish_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 4
--   ), fish_buyer_5_list AS ( -- 列出購買五檔魚慶典的人
--         SELECT UserID
--         FROM fish_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 5
--   )
  
  
-- --    final_table_by_missionid AS ( -- 購買魚慶典檔期的玩家們的門檻任務進度及其達到最高門檻
-- SELECT * , 
--       CASE WHEN label = 1 THEN MissionPriority 
--            ELSE　NULL 
--       END AS max_completelevel, 
--       'fish_festival' AS MissionBookMark,
--       CASE WHEN UserID IN (SELECT * FROM fish_buyer_1_list) THEN 1
--            WHEN UserID IN (SELECT * FROM fish_buyer_2_list) THEN 2
--            WHEN UserID IN (SELECT * FROM fish_buyer_3_list) THEN 3
--            WHEN UserID IN (SELECT * FROM fish_buyer_4_list) THEN 4
--            WHEN UserID IN (SELECT * FROM fish_buyer_5_list) THEN 5 
--       END AS user_fish_buycount
-- FROM(
--     SELECT *, ROW_NUMBER() OVER(PARTITION BY UserID, ActivityStartTime ORDER BY MissionPriority DESC) AS label 
--     FROM fish_buyer_completeLog
--     ) temp_table;
-- --   )

-- -- -- 目標: 列出魚慶典購買玩家的過往行為(是否有活躍在玩: active_session、是否只買魚慶典 battlepassBuyLog)
-- WITH 
--   fish_info AS ( -- 找出魚慶典的所有 eventname (因為BattlePassBuyLog只有eventname)
--     SELECT DISTINCT EventName, CONCAT('bp_', EventName) AS BattlePassID
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE 
--       BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74')
--   ), fish_bp_buyerID AS ( -- 找出有購買魚慶典BP的玩家(魚慶典共有三檔 11/2 11/9 11/16 11/23 11/30)，列出有購買的玩家、買哪一檔、買的日期
--         SELECT DISTINCT UserID, BattlePassID, 
--           CASE 
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--             ELSE DATE('2025-11-30')
--           END AS ActivityStartTime,
--           CONCAT(UserID, '_', CASE WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--                               ELSE DATE('2025-11-30') END) 
--           AS buyer_period, -- buyerid與其購買的檔期，才能從completelog篩出購買該檔期玩家的行為
--           EXTRACT(DATE FROM TimeStamp_Seconds(EventTime) AT TIME ZONE 'Asia/Taipei') AS order_date,
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE BattlePassID IN (SELECT BattlePassID FROM fish_info)
--         ORDER BY UserID DESC
--   ), fish_bp_buyerID2 AS ( -- buyerid、其所有購買的魚慶典中最早檔期、購買魚慶典最早檔期的訂單日期、購買魚慶典的檔期數量
--     SELECT UserID, MIN(order_date) AS EarliestOrderDate, MIN(ActivityStartTime) AS EarliestActivityStartTime, COUNT(*) AS fish_bp_buycounts
--     FROM fish_bp_buyerID
--     GROUP BY UserID
--   ), fish_bpbuyer_purchasehistory AS ( -- 有購買魚慶典的玩家在首次購買魚慶典的前七天內，除了魚慶典是否有買其他BP: 若只有買此次可能屬套利
--     SELECT temp.UserID,
--                 SUM(CASE WHEN EXTRACT(DATE FROM TimeStamp_Seconds(EventTime) AT TIME ZONE 'Asia/Taipei') BETWEEN DATE_SUB(EarliestOrderDate, INTERVAL 7 DAY) 
--             AND EarliestOrderDate THEN 1 ELSE 0 END) - 1 AS fishbought_previous7days_buyrecords -- 扣掉一是因為要算除了魚慶典外的其他BP
--     FROM
--       (
--         SELECT *
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE UserID in (SELECT UserID FROM fish_bp_buyerID)
--               AND DATE(TIMESTAMP_SECONDS(EventTime)) >= DATE('2025-10-25') 
--       ) AS temp -- 提升效能: 縮小join時的資料列數
--     LEFT JOIN fish_bp_buyerID2 fbbid2
--         ON temp.UserID = fbbid2.UserID
--     GROUP BY temp.UserID
      
--   ), fish_bpbuyer_activestatus as ( -- 有購買魚慶典的玩家在活動開始七天前至購買日當天的活躍次數: 若都沒活躍而是因為活動才出現則代表套利玩家 
    
--     SELECT temp2.UserID,
--            SUM(CASE WHEN PARSE_DATE('%Y%m%d', CAST(LoginDate AS STRING)) BETWEEN DATE_SUB(EarliestOrderDate, INTERVAL 7 DAY) AND EarliestOrderDate THEN 1 ELSE 0 END) - 1 AS fishbought_previous7days_activesession -- 扣掉一是因為要算除了買魚慶典那次以外的active session
--     FROM
--     (
--       SELECT *
--       FROM `rd7-data-big-query.bklog.SessionActive`
--       WHERE  PARSE_DATE('%Y%m%d', CAST(LoginDate AS STRING)) >= DATE('2025-10-25')
--             AND UserID in (SELECT UserID FROM fish_bp_buyerID2)
--     )  AS temp2 -- 提升效能: 縮小join時的資料列數
--     LEFT JOIN fish_bp_buyerID2 fbbid2
--       ON temp2.UserID = fbbid2.UserID
--     GROUP BY temp2.UserID
--   )

-- SELECT *
-- FROM fish_bp_buyerID2 AS fbbID2
-- LEFT JOIN fish_bpbuyer_purchasehistory fbph
--   USING (UserID)
-- LEFT JOIN fish_bpbuyer_activestatus
--   USING (UserID)
-- ;



-- -- ***************************** 獵慶典分隔線 **************************************
-- -- 目標: 列出獵慶典付費玩家的活動完成狀況

-- WITH 
--   hunt_info AS ( -- 找出獵慶典的所有 eventname (因為BattlePassBuyLog只有eventname)
--     SELECT DISTINCT EventName, CONCAT('bp_', EventName) AS BattlePassID
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE 
--       BQDate >= '2025-11-01'
--       and BatchID = '2025-11-02#59c76'
--   ), hunt_bp_buyerID AS ( -- 找出有購買獵慶典BP的玩家(獵慶典共有三檔 11/2 11/9 11/16 11/23 11/30)，列出有購買的玩家和買哪一檔
--         SELECT DISTINCT UserID, BattlePassID, 
--           CASE 
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--             ELSE DATE('2025-11-30')
--               END AS ActivityStartTime,
--           CONCAT(UserID, '_', CASE WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--                               ELSE DATE('2025-11-30') END) 
--           AS buyer_period -- buyerid與其購買的檔期，才能從completelog篩出購買該檔期玩家的行為
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE BattlePassID IN (SELECT BattlePassID FROM hunt_info)
--         ORDER BY UserID DESC
--   ), hunt_completeLog AS (-- 整理獵慶典活動Log，為了接下來能找出購買特定檔期玩家的missioncompletelog
--         SELECT *,
--                EXTRACT(DATETIME FROM TIMESTAMP_SECONDS(EventTime) AT TIME ZONE 'Asia/Taipei') AS completed_time, 
--                datetime(TIMESTAMP_SECONDS(EventTime), 'UTC+8'),
--                EXTRACT(DATE FROM TIMESTAMP_SECONDS(StartTime) AT TIME ZONE 'Asia/Taipei') AS ActivityStartTime, 
--                CONCAT(UserID,'_', EXTRACT(DATE FROM TIMESTAMP_SECONDS(StartTime) AT TIME ZONE 'Asia/Taipei')) AS user_period 
--         FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
--         WHERE BatchID = '2025-11-02#59c76'
--   ), hunt_buyer_completeLog AS (-- 篩選出有購買BP玩家的任務完成資訊。因獵慶典有三檔，只選出玩家買BP該檔的紀錄，若買第二檔那就只篩出第二檔的資料
--         SELECT UserID, VipLV, completed_time, ActivityStartTime, MissionID, (MissionPriority + 1) AS MissionPriority 
--         FROM hunt_completeLog
--         WHERE user_period IN (SELECT buyer_period FROM hunt_bp_buyerID)
--         ORDER BY UserID DESC, ActivityStartTime DESC, MissionPriority DESC
--   ), hunt_buyer_1_list AS ( -- 列出購買兩檔獵慶典的人
--         SELECT UserID
--         FROM hunt_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 1
--   ), hunt_buyer_2_list AS ( -- 列出購買兩檔獵慶典的人
--         SELECT UserID
--         FROM hunt_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 2
--   ), hunt_buyer_3_list AS ( -- 列出購買三檔獵慶典的人
--         SELECT UserID
--         FROM hunt_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 3
--   ), hunt_buyer_4_list AS ( -- 列出購買四檔獵慶典的人
--         SELECT UserID
--         FROM hunt_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 4
--   ), hunt_buyer_5_list AS ( -- 列出購買五檔獵慶典的人
--         SELECT UserID
--         FROM hunt_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 5
--   )
  
  
-- --    final_table_by_missionid AS ( -- 購買獵慶典檔期的玩家們的門檻任務進度及其達到最高門檻
-- SELECT * , 
--       CASE WHEN label = 1 THEN MissionPriority 
--            ELSE　NULL 
--       END AS max_completelevel, 
--       'hunt_festival' AS MissionBookMark,
--       CASE WHEN UserID IN (SELECT * FROM hunt_buyer_1_list) THEN 1
--            WHEN UserID IN (SELECT * FROM hunt_buyer_2_list) THEN 2
--            WHEN UserID IN (SELECT * FROM hunt_buyer_3_list) THEN 3
--            WHEN UserID IN (SELECT * FROM hunt_buyer_4_list) THEN 4
--            WHEN UserID IN (SELECT * FROM hunt_buyer_5_list) THEN 5 
--       END AS user_hunt_buycount
-- FROM(
--     SELECT *, ROW_NUMBER() OVER(PARTITION BY UserID, ActivityStartTime ORDER BY MissionPriority DESC) AS label 
--     FROM hunt_buyer_completeLog
--     ) temp_table;
-- --   )


-- -- -- 目標: 列出獵慶典購買玩家的過往行為(是否有活躍在玩、是否只買獵慶典)
-- WITH 
--   hunt_info AS ( -- 找出獵慶典的所有 eventname (因為BattlePassBuyLog只有eventname)
--     SELECT DISTINCT EventName, CONCAT('bp_', EventName) AS BattlePassID
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE 
--       BatchID = '2025-11-02#59c76'
--   ), hunt_bp_buyerID AS ( -- 找出有購買獵慶典BP的玩家(獵慶典共有三檔 11/2 11/9 11/16 11/23 11/30)，列出有購買的玩家、買哪一檔、買的日期
--         SELECT DISTINCT UserID, BattlePassID, 
--           CASE 
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--             ELSE DATE('2025-11-30')
--           END AS ActivityStartTime,
--           CONCAT(UserID, '_', CASE WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--                               ELSE DATE('2025-11-30') END) 
--           AS buyer_period, -- buyerid與其購買的檔期，才能從completelog篩出購買該檔期玩家的行為
--           EXTRACT(DATE FROM TimeStamp_Seconds(EventTime) AT TIME ZONE 'Asia/Taipei') AS order_date,
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE BattlePassID IN (SELECT BattlePassID FROM hunt_info)
--         ORDER BY UserID DESC
--   ), hunt_bp_buyerID2 AS ( -- buyerid、其所有購買的獵慶典中最早檔期、購買獵慶典最早檔期的訂單日期、購買獵慶典的檔期數量
--     SELECT UserID, MIN(order_date) AS EarliestOrderDate, MIN(ActivityStartTime) AS EarliestActivityStartTime, COUNT(*) AS hunt_bp_buycounts
--     FROM hunt_bp_buyerID
--     GROUP BY UserID
--   ), hunt_bpbuyer_purchasehistory AS ( -- 有購買獵慶典的玩家在首次購買獵慶典的前七天內，除了獵慶典是否有買其他BP: 若只有買此次可能屬套利
--     SELECT temp.UserID,
--                 SUM(CASE WHEN EXTRACT(DATE FROM TimeStamp_Seconds(EventTime) AT TIME ZONE 'Asia/Taipei') BETWEEN DATE_SUB(EarliestOrderDate, INTERVAL 7 DAY) 
--             AND EarliestOrderDate THEN 1 ELSE 0 END) - 1 AS huntbought_previous7days_buyrecords -- 扣掉一是因為要算除了獵慶典外的其他BP
--     FROM
--       (
--         SELECT *
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE UserID in (SELECT UserID FROM hunt_bp_buyerID)
--               AND DATE(TIMESTAMP_SECONDS(EventTime)) >= DATE('2025-10-25') 
--       ) AS temp -- 提升效能: 縮小join時的資料列數
--     LEFT JOIN hunt_bp_buyerID2 fbbid2
--         ON temp.UserID = fbbid2.UserID
--     GROUP BY temp.UserID
      
--   ), hunt_bpbuyer_activestatus as ( -- 有購買獵慶典的玩家在活動開始七天前至購買日當天的活躍次數: 若都沒活躍而是因為活動才出現則代表套利玩家 
    
--     SELECT temp2.UserID,
--            SUM(CASE WHEN PARSE_DATE('%Y%m%d', CAST(LoginDate AS STRING)) BETWEEN DATE_SUB(EarliestOrderDate, INTERVAL 7 DAY) AND EarliestOrderDate THEN 1 ELSE 0 END) - 1 AS huntbought_previous7days_activesession -- 扣掉一是因為要算除了買獵慶典那次以外的active session
--     FROM
--     (
--       SELECT *
--       FROM `rd7-data-big-query.bklog.SessionActive`
--       WHERE  PARSE_DATE('%Y%m%d', CAST(LoginDate AS STRING)) >= DATE('2025-10-25')
--             AND UserID in (SELECT UserID FROM hunt_bp_buyerID2)
--     )  AS temp2 -- 提升效能: 縮小join時的資料列數
--     LEFT JOIN hunt_bp_buyerID2 fbbid2
--       ON temp2.UserID = fbbid2.UserID
--     GROUP BY temp2.UserID
--   )

-- SELECT *
-- FROM hunt_bp_buyerID2 AS fbbID2
-- LEFT JOIN hunt_bpbuyer_purchasehistory fbph
--   USING (UserID)
-- LEFT JOIN hunt_bpbuyer_activestatus
--   USING (UserID);


-- -- ***************************** 惡慶典分隔線 **************************************
-- -- 目標: 列出惡慶典付費玩家的活動完成狀況

-- WITH 
--   devil_info AS ( -- 找出惡慶典的所有 eventname (因為BattlePassBuyLog只有eventname)
--     SELECT DISTINCT EventName, CONCAT('bp_', EventName) AS BattlePassID
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE 
--       BQDate >= '2025-11-01'
--       and BatchID =  '2025-11-02#47edf'
--   ), devil_bp_buyerID AS ( -- 找出有購買惡慶典BP的玩家(惡慶典共有三檔 11/2 11/9 11/16 11/23 11/30)，列出有購買的玩家和買哪一檔
--         SELECT DISTINCT UserID, BattlePassID, 
--           CASE 
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--             ELSE DATE('2025-11-30')
--               END AS ActivityStartTime,
--           CONCAT(UserID, '_', CASE WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--                               ELSE DATE('2025-11-30') END) 
--           AS buyer_period -- buyerid與其購買的檔期，才能從completelog篩出購買該檔期玩家的行為
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE BattlePassID IN (SELECT BattlePassID FROM devil_info)
--         ORDER BY UserID DESC
--   ), devil_completeLog AS (-- 整理惡慶典活動Log，為了接下來能找出購買特定檔期玩家的missioncompletelog
--         SELECT *,
--                EXTRACT(DATETIME FROM TIMESTAMP_SECONDS(EventTime) AT TIME ZONE 'Asia/Taipei') AS completed_time, 
--                datetime(TIMESTAMP_SECONDS(EventTime), 'UTC+8'),
--                EXTRACT(DATE FROM TIMESTAMP_SECONDS(StartTime) AT TIME ZONE 'Asia/Taipei') AS ActivityStartTime, 
--                CONCAT(UserID,'_', EXTRACT(DATE FROM TIMESTAMP_SECONDS(StartTime) AT TIME ZONE 'Asia/Taipei')) AS user_period 
--         FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
--         WHERE BatchID =  '2025-11-02#47edf'
--   ), devil_buyer_completeLog AS (-- 篩選出有購買BP玩家的任務完成資訊。因惡慶典有三檔，只選出玩家買BP該檔的紀錄，若買第二檔那就只篩出第二檔的資料
--         SELECT UserID, VipLV, completed_time, ActivityStartTime, MissionID, (MissionPriority + 1) AS MissionPriority 
--         FROM devil_completeLog
--         WHERE user_period IN (SELECT buyer_period FROM devil_bp_buyerID)
--         ORDER BY UserID DESC, ActivityStartTime DESC, MissionPriority DESC
--   ), devil_buyer_1_list AS ( -- 列出購買兩檔惡慶典的人
--         SELECT UserID
--         FROM devil_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 1
--   ), devil_buyer_2_list AS ( -- 列出購買兩檔惡慶典的人
--         SELECT UserID
--         FROM devil_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 2
--   ), devil_buyer_3_list AS ( -- 列出購買三檔惡慶典的人
--         SELECT UserID
--         FROM devil_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 3
--   ), devil_buyer_4_list AS ( -- 列出購買四檔惡慶典的人
--         SELECT UserID
--         FROM devil_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 4
--   ), devil_buyer_5_list AS ( -- 列出購買五檔惡慶典的人
--         SELECT UserID
--         FROM devil_buyer_completeLog
--         GROUP BY UserID
--         HAVING COUNT(DISTINCT ActivityStartTime) = 5
--   )
  
  
-- --    final_table_by_missionid AS ( -- 購買惡慶典檔期的玩家們的門檻任務進度及其達到最高門檻
-- SELECT * , 
--       CASE WHEN label = 1 THEN MissionPriority 
--            ELSE　NULL 
--       END AS max_completelevel, 
--       'devil_festival' AS MissionBookMark,
--       CASE WHEN UserID IN (SELECT * FROM devil_buyer_1_list) THEN 1
--            WHEN UserID IN (SELECT * FROM devil_buyer_2_list) THEN 2
--            WHEN UserID IN (SELECT * FROM devil_buyer_3_list) THEN 3
--            WHEN UserID IN (SELECT * FROM devil_buyer_4_list) THEN 4
--            WHEN UserID IN (SELECT * FROM devil_buyer_5_list) THEN 5 
--       END AS user_devil_buycount
-- FROM(
--     SELECT *, ROW_NUMBER() OVER(PARTITION BY UserID, ActivityStartTime ORDER BY MissionPriority DESC) AS label 
--     FROM devil_buyer_completeLog
--     ) temp_table;
-- --   )

-- -- -- 目標: 列出惡慶典購買玩家的過往行為(是否有活躍在玩、是否只買惡慶典)
-- WITH 
--   devil_info AS ( -- 找出惡慶典的所有 eventname (因為BattlePassBuyLog只有eventname)
--     SELECT DISTINCT EventName, CONCAT('bp_', EventName) AS BattlePassID
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE 
--       BatchID =  '2025-11-02#47edf'
--   ), devil_bp_buyerID AS ( -- 找出有購買惡慶典BP的玩家(惡慶典共有三檔 11/2 11/9 11/16 11/23 11/30)，列出有購買的玩家、買哪一檔、買的日期
--         SELECT DISTINCT UserID, BattlePassID, 
--           CASE 
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--             WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--             ELSE DATE('2025-11-30')
--           END AS ActivityStartTime,
--           CONCAT(UserID, '_', CASE WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-09') THEN DATE('2025-11-02')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-16') THEN DATE('2025-11-09')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-23') THEN DATE('2025-11-16')
--                                    WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) < DATE('2025-11-30') THEN DATE('2025-11-23')
--                               ELSE DATE('2025-11-30') END) 
--           AS buyer_period, -- buyerid與其購買的檔期，才能從completelog篩出購買該檔期玩家的行為
--           EXTRACT(DATE FROM TimeStamp_Seconds(EventTime) AT TIME ZONE 'Asia/Taipei') AS order_date,
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE BattlePassID IN (SELECT BattlePassID FROM devil_info)
--         ORDER BY UserID DESC
--   ), devil_bp_buyerID2 AS ( -- buyerid、其所有購買的惡慶典中最早檔期、購買惡慶典最早檔期的訂單日期、購買惡慶典的檔期數量
--     SELECT UserID, MIN(order_date) AS EarliestOrderDate, MIN(ActivityStartTime) AS EarliestActivityStartTime, COUNT(*) AS devil_bp_buycounts
--     FROM devil_bp_buyerID
--     GROUP BY UserID
--   ), devil_bpbuyer_purchasehistory AS ( -- 有購買惡慶典的玩家在首次購買惡慶典的前七天內，除了惡慶典是否有買其他BP: 若只有買此次可能屬套利
--     SELECT temp.UserID,
--                 SUM(CASE WHEN EXTRACT(DATE FROM TimeStamp_Seconds(EventTime) AT TIME ZONE 'Asia/Taipei') BETWEEN DATE_SUB(EarliestOrderDate, INTERVAL 7 DAY) 
--             AND EarliestOrderDate THEN 1 ELSE 0 END) - 1 AS devilbought_previous7days_buyrecords -- 扣掉一是因為要算除了惡慶典外的其他BP
--     FROM
--       (
--         SELECT *
--         FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--         WHERE UserID in (SELECT UserID FROM devil_bp_buyerID)
--               AND DATE(TIMESTAMP_SECONDS(EventTime)) >= DATE('2025-10-25') 
--       ) AS temp -- 提升效能: 縮小join時的資料列數
--     LEFT JOIN devil_bp_buyerID2 fbbid2
--         ON temp.UserID = fbbid2.UserID
--     GROUP BY temp.UserID
      
--   ), devil_bpbuyer_activestatus as ( -- 有購買惡慶典的玩家在活動開始七天前至購買日當天的活躍次數: 若都沒活躍而是因為活動才出現則代表套利玩家 
    
--     SELECT temp2.UserID,
--            SUM(CASE WHEN PARSE_DATE('%Y%m%d', CAST(LoginDate AS STRING)) BETWEEN DATE_SUB(EarliestOrderDate, INTERVAL 7 DAY) AND EarliestOrderDate THEN 1 ELSE 0 END) - 1 AS devilbought_previous7days_activesession -- 扣掉一是因為要算除了買惡慶典那次以外的active session
--     FROM
--     (
--       SELECT *
--       FROM `rd7-data-big-query.bklog.SessionActive`
--       WHERE  PARSE_DATE('%Y%m%d', CAST(LoginDate AS STRING)) >= DATE('2025-10-25')
--             AND UserID in (SELECT UserID FROM devil_bp_buyerID2)
--     )  AS temp2 -- 提升效能: 縮小join時的資料列數
--     LEFT JOIN devil_bp_buyerID2 fbbid2
--       ON temp2.UserID = fbbid2.UserID
--     GROUP BY temp2.UserID
--   )

-- SELECT *
-- FROM devil_bp_buyerID2 AS fbbID2
-- LEFT JOIN devil_bpbuyer_purchasehistory fbph
--   USING (UserID)
-- LEFT JOIN devil_bpbuyer_activestatus
--   USING (UserID)
```

## [Analysis] 新人第一個月期末
**描述：** 十月十一月BP主要收入來源的慶典BP風險分析2

```sql
-- 目的: 找出為甚麼三慶典套利玩家都玩到中間的關卡
-- 'AA_魚慶典_排除負貢獻_七日_CN_v23456', 'AA_獵慶典_七日_CN_v23456', 'AA_惡慶典_七日_CN_v23456'
-- ('2025-11-02#20f83', '2025-11-23#97d74'), '2025-11-02#59c76', '2025-11-02#47edf'
with 
-------------------惡慶典始--------------------- 
     devil_buyer_buyround_flag as ( -- 惡慶典誰買了哪個round、該買家是否為風險玩家
      select a.*, case when c.UserID is null then 0 else 1 end as flag
      from (
                  select UserID, 
                         BattlePassID,
                         concat(UserID, BattlePassID) as buyer_buyround,
                         CASE 
                              WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) = DATE('2025-11-02') THEN DATE('2025-11-02')
                              WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) = DATE('2025-11-09') THEN DATE('2025-11-09')
                              WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) = DATE('2025-11-16') THEN DATE('2025-11-16')
                              WHEN PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(BattlePassID, r'_(\d{8})_')) = DATE('2025-11-23') THEN DATE('2025-11-23')
                         ELSE DATE('2025-11-30')
                              END AS which_round,
                        
                  from `rd7-data-big-query.bklog.BattlePassBuyLog`
                  where BQDate > '2025-11-01' and BattlePassID IN ( select distinct concat('bp_', EventName) 
                                                                    from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
                                                                    where BQDate > '2025-11-01' and BatchID = '2025-11-02#47edf')
            ) a
      left join(
                  select distinct UserID
                  from `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
            ) as c
            on a.UserID=c.UserID
     
     
      ), devil_buyer_maxlevel as ( -- devil_buyer_buyround_flag 加上惡慶典買家在買的那期最高玩到第幾關     
      select a.*, b.EventName, b.max_complete_level
      from devil_buyer_buyround_flag a 
      left join 
            (
                  SELECT UserID, EventName, concat(UserID, 'bp_', EventName) as user_completeround, MAX(MissionPriority) + 1 AS max_complete_level -- 有買惡慶典的在所有惡慶典rounds的最高等級
                  FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
                  WHERE BQDate > '2025-11-01'
                        AND BatchID = '2025-11-02#47edf'
                        AND UserID IN (
                              select distinct UserID 
                              from devil_buyer_buyround_flag
                              )
                  GROUP BY 1, 2, 3
            ) b
            
            on a.buyer_buyround = b.user_completeround
      ), devil_buyer_reward  as ( -- 惡慶典買家在買的那期領到的免費獎勵與黃金獎勵
      select UserID, EventName, sum( case when BattlePass = 0 then RewardValue else 0 end ) as basic_reward,  sum( case when BattlePass = 1 then RewardValue else 0 end ) as gold_reward
      from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
      where EventName = (
            select distinct substr(BattlePassID, 4) as EventName 
            from devil_buyer_buyround_flag  
            order by EventName 
            limit 1
            )
            AND UserID in (
                  select distinct UserID 
                  from devil_buyer_buyround_flag 
                  where which_round = (
                        select distinct which_round 
                        from devil_buyer_buyround_flag 
                        order by which_round 
                        limit 1)
                        ) 
            AND RewardType = 1
      group by 1, 2
      UNION ALL
      select UserID, EventName, sum( case when BattlePass = 0 then RewardValue else 0 end ) as basic_reward,  sum( case when BattlePass = 1 then RewardValue else 0 end ) as gold_reward
      from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
      where EventName = (select distinct substr(BattlePassID, 4) as EventName from devil_buyer_buyround_flag  order by EventName limit 1 offset 1)
      AND
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = (select distinct which_round from devil_buyer_buyround_flag order by which_round limit 1 offset 1)) AND
            RewardType = 1
      group by 1, 2
      UNION ALL
      select UserID, EventName, sum( case when BattlePass = 0 then RewardValue else 0 end ) as basic_reward,  sum( case when BattlePass = 1 then RewardValue else 0 end ) as gold_reward
      from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
      where EventName = (select distinct substr(BattlePassID, 4) as EventName from devil_buyer_buyround_flag  order by EventName limit 1 offset 2)AND
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = (select distinct which_round from devil_buyer_buyround_flag order by which_round limit 1 offset 2)) AND
            RewardType = 1
      group by 1, 2
      UNION ALL
      select UserID, EventName, sum( case when BattlePass = 0 then RewardValue else 0 end ) as basic_reward,  sum( case when BattlePass = 1 then RewardValue else 0 end ) as gold_reward
      from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
      where EventName = (select distinct substr(BattlePassID, 4) as EventName from devil_buyer_buyround_flag  order by EventName limit 1 offset 3)AND
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = (select distinct which_round from devil_buyer_buyround_flag order by which_round limit 1 offset 3)) AND
            RewardType = 1
      group by 1, 2
      ), devil_buyer_ingame AS ( -- 惡慶典玩家在購買當期BP時，實際在魚機遊玩的數據
      select UserID, DATE('2025-11-02') as which_round, SUM(TotalBet) as total_bet, SUM(TotalWin) as total_win, ROUND(AVG(BetPerShoot)) as avg_bet_pershoot, SUM(TotalBetTimes) as total_bet_times
      from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog` 
      where BQDate BETWEEN '2025-11-02' AND '2025-11-08' and 
            TableTypeID = 9 and 
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = '2025-11-02')
      group by 1
      UNION ALL
      select UserID, DATE('2025-11-09') as which_round, SUM(TotalBet) as total_bet, SUM(TotalWin) as total_win, ROUND(AVG(BetPerShoot)) as avg_bet_pershoot, SUM(TotalBetTimes) as total_bet_times
      from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog` 
      where BQDate BETWEEN '2025-11-09' AND '2025-11-15' and 
            TableTypeID = 9 and 
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = '2025-11-09')
      group by 1
      UNION ALL
      select UserID, DATE('2025-11-16') as which_round, SUM(TotalBet) as total_bet, SUM(TotalWin) as total_win, ROUND(AVG(BetPerShoot)) as avg_bet_pershoot, SUM(TotalBetTimes) as total_bet_times
      from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog` 
      where BQDate BETWEEN '2025-11-16' AND '2025-11-22' and 
            TableTypeID = 9 and 
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = '2025-11-16')
      group by 1
      UNION ALL
      select UserID, DATE('2025-11-23') as which_round, SUM(TotalBet) as total_bet, SUM(TotalWin) as total_win, ROUND(AVG(BetPerShoot)) as avg_bet_pershoot, SUM(TotalBetTimes) as total_bet_times
      from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog` 
      where BQDate BETWEEN '2025-11-23' AND '2025-11-29' and 
            TableTypeID = 9 and 
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = '2025-11-23')
      group by 1
      UNION ALL
      select UserID, DATE('2025-11-30') as which_round, SUM(TotalBet) as total_bet, SUM(TotalWin) as total_win, ROUND(AVG(BetPerShoot)) as avg_bet_pershoot, SUM(TotalBetTimes) as total_bet_times
      from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog` 
      where BQDate BETWEEN '2025-11-30' AND '2025-12-06' and 
            TableTypeID = 9 and 
            UserID in (select distinct UserID from devil_buyer_buyround_flag where which_round = '2025-11-30')
      group by 1
      )

select 'devil' as MissionBookMark, m.UserID, m.BattlePassID, m.EventName, m.which_round, m.flag, m.max_complete_level,
      r.basic_reward, r.gold_reward, i.total_bet, i.total_win, i.total_bet_times, i.avg_bet_pershoot 
from devil_buyer_maxlevel m
join devil_buyer_reward r
      on  m.UserID = r.UserID and m.EventName = r.EventName
join devil_buyer_ingame i
      on m.UserID = i.UserID  and m.which_round = i.which_round










;
--------- 以下為查詢惡慶典風險玩家的遊玩時間與購買惡慶典時間，為判斷是玩到第幾關才買
select UserID, DATETIME(TIMESTAMP_SECONDS(LastEventTime)) as last_bet_time,  SUM(TotalBet) as total_bet, SUM(TotalWin) as total_win, 
       SUM(TotalBetTimes) as total_bet_time, sum(CancelBet) as CancelBet
from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog` 
where BQDate BETWEEN '2025-11-01' AND '2025-11-25' and 
      TableTypeID = 9 and 
      UserID in (62808043,106033403,106094009,106304247,106384953,106431718,106474953,106485462,106502823,106517265,106536821,106544675,106550565)
group by 1, 2
order by UserID, last_bet_time desc ;



select UserID, DATETIME(TIMESTAMP_SECONDS(EventTime)) as buy_time
from `rd7-data-big-query.bklog.BattlePassBuyLog`
where BattlePassID in (select distinct concat('bp_', EventName) from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` where BatchID = '2025-11-02#47edf')  and 
      UserID in (62808043,106033403,106094009,106304247,106384953,106431718,106474953,106485462,106502823,106517265,106536821,106544675,106550565)
order by UserID, buy_time desc;








-- WITH bp_info AS (
--     SELECT DISTINCT MissionBookMark, CONCAT('bp_', EventName) AS BattlePassID, ActivityStartTime, ActivityEndTime, MissionPriority, TargetTimes, VipLV, MissionValue, BPMissionValue, MissionCardValue, BPMissionCardValue
--     FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--     WHERE BQDate BETWEEN '2025-11-01' AND '2025-11-23'
--           AND BatchID in  ('2025-11-02#20f83', '2025-11-23#97d74', '2025-11-02#59c76', '2025-11-02#47edf')
--   ), bp_buyerinfo AS ( -- main table: 誰買了哪一檔期、是否曾為風險人物
    
--     SELECT a.UserID, VipLV, BattlePassID, CONCAT(a.UserID, BattlePassID) AS buyer_item, CASE WHEN b.UserID IS NOT NULL THEN 1 ELSE 0 END AS risk_user
--     FROM (
--       SELECT UserID, VipLV, BattlePassID, CONCAT(UserID, BattlePassID) AS buyer_item
--       FROM `rd7-data-big-query.bklog.BattlePassBuyLog`
--       WHERE BQDate BETWEEN '2025-11-01' AND '2025-11-23'
--             AND BattlePassID IN (select distinct BattlePassID from bp_info)
--     ) a
--     LEFT JOIN 
--       (
--         SELECT DISTINCT UserID
--         FROM `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
--       ) as b
--       ON a.UserID = b.UserID

--   ), bp_buyerProgress AS ( -- 只要有購買任一檔的人的所有活動進度，故包含了沒買的活動進度
--     SELECT UserID, EventName, CONCAT(UserID, 'bp_', EventName) AS user_item, MAX(MissionPriority) AS max_complete_level 
--     FROM `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
--     WHERE BQDate > '2025-11-01'
--           AND BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74', '2025-11-02#59c76', '2025-11-02#47edf')
--           AND UserID IN (SELECT DISTINCT UserID FROM bp_buyerinfo)
--     GROUP BY 1, 2, 3
--  )--, bp_buyerReward AS ( 
--   --   SELECT UserID, EventName, UserItem, SUM(CASE WHEN BattlePass = 0 THEN RewardValue ELSE 0 END) AS free_rebate, SUM(CASE WHEN BattlePass = 1 THEN RewardValue ELSE 0 END) AS buy_rebate
--   --   FROM (
--   --         SELECT *, CONCAT(UserID, 'bp_', EventName) AS UserItem
--   --         FROM `rd7-data-big-query.bklog.ActivityMissionRewardLog` 
--   --         WHERE BQDate >= '2025-11-01' 
--   --               AND  UserID IN (SELECT DISTINCT UserID FROM bp_buyerinfo)
--   --               AND BatchID IN ('2025-11-02#20f83', '2025-11-23#97d74', '2025-11-02#59c76', '2025-11-02#47edf')
--   --               AND RewardType = 1
--   --         ) a
--   --   RIGHT JOIN 
--   --        (
--   --         SELECT　buyer_item 
--   --         FROM bp_buyerinfo
--   --         ) b
--   --     ON a.UserItem = b.buyer_item
--   --   GROUP BY 1, 2, 3
--   -- )

--   SELECT bbi.UserID, bbi.risk_user, bbi.VipLV, bbi.BattlePassID, bbp.max_complete_level, missionbookmark, ActivityStartTime, ActivityEndTime,
--         SUM(CASE WHEN MissionPriority <= bbp.max_complete_level AND bbi.VipLV = bp_info.VipLV THEN  MissionValue + BPMissionValue - MissionCardValue - BPMissionCardValue END) AS rebate
--   FROM bp_buyerinfo bbi
--   LEFT JOIN bp_buyerProgress bbp
--     ON bbi.buyer_item = bbp.user_item
--   LEFT JOIN bp_info
--    ON bbi.BattlePassID = bp_info.BattlePassID
--   GROUP BY bbi.UserID, risk_user, bbi.VipLV, bbi.BattlePassID, bbp.max_complete_level, missionbookmark, ActivityStartTime, ActivityEndTime
```

## [Analysis] 12月1月平台給予、BP基本獎勵
**描述：** Issue 1: 免費BP獲得在12/2, 12/19, 12/27, 12/31跟 1/2, 1/3, 1/4 漲高
Issue 2: 平台給予12月下旬攀升: 11月下旬跟12月下旬各個Category的平台給予狀況，找出是哪個Category高漲

```sql
-- Issue 1: 免費BP獲得在12/2, 12/19, 12/27, 12/31跟 1/2, 1/3, 1/4 漲高
with freereward as (
  select distinct BQDate, UserID, EventName, MissionPriority + 1 as MissionPriority, RewardValue
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
  where BQDate IN (
                  --  '2025-12-02',
                  --  '2025-12-19', 
                  --  '2025-12-27',
                  --  '2025-12-31',
                  --  '2026-01-02',
                  --  '2026-01-03',
                   '2026-01-04'
                  )  and
        BattlePass  = 0 and
        RewardType = 1 and
        Country = 'CN'
), freereward_missionbookmark as (
  select *
  from freereward a
  left join  (
              select EventName, MissionBookMark 
              from`rd7-data-big-query.preprocessed_bklog.MissionList` 
              where ActivityStartTime >= '2025-12-01' or ActivityEndTime >= '2025-12-01'
             ) b
    on a.EventName = b.EventName
), targetuser as (
  select UserID, NewUserTag, UserTag,
         case when UserTag != NewUserTag then 1 else 0 end as status_change
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  where BQDate = '2026-01-01' and
        -- NewUserTag IN  ('無客', '中客') and
        Country = 'CN'
)

select BQDate, 
       MissionBookMark,
      --  a.UserID,
       b.NewUserTag,
       count(distinct a.UserID) as usercounts,
       sum(RewardValue) as freereward_taken,
       -- max(MissionPriority) as reached_level
from freereward_missionbookmark a
inner join targetuser b
  on a.UserID = b.UserID
group by 1, 2, 3
order by MissionBookMark, freereward_taken desc
;




-- Issue 2: 平台給予12月下旬攀升: 11月下旬跟12月下旬各個Category的平台給予狀況，找出是哪個Category高漲
with targettime as (
select *
from `rd7-data-big-query.bklog.SessionCoinLog`
where BQDate >= '2026-01-01' and  
      UserID in (select distinct UserID 
                 from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
                 where BQDate >= '2026-01-01')
)

select -- BQDate, 
       b.ReasonName_CHT, Category , sum(TotalCoinAwarded) as totalaward
from targettime a
left join `rd7-data-big-query.kuochinfu.DataTeamCoinReason` b
  on a.CoinReason = b.CoinReasonId
where Category = '平台給予'
group by 1, 2
; 

-- -- Issue: 免費BP獲得在2026/1/2，本月負貢獻跟本月無客暴漲
-- with targetuser as (
--   select UserID, NewUserTag, UserTag,
--          case when UserTag != NewUserTag then 1 else 0 end as status_change
--   from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
--   where BQDate = '2026-01-01' and
--         NewUserTag in ('無客', '負貢獻') and
--         Country = 'CN'
-- ), freereward as (
--   select *
--   from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
--   where BQDate = '2026-01-02' and
--         BattlePass  = 0 and
--         RewardType = 1 and
--         Country = 'CN'
-- )

-- select a.EventName,
--        c.MissionBookMark,
--        b.UserID, 
--        b.UserTag, 
--        b.NewUserTag,
--        b.status_change,
--        sum(RewardValue) as rewardvalue
-- from freereward a 
-- inner join targetuser b
--   on a.UserID = b.UserID
-- left join (
--           select distinct EventName, MissionBookMark
--           from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--           where BQDate = '2026-01-02' 
--           ) c
--   on a.EventName = c.EventName
-- group by 1, 2, 3, 4, 5, 6
-- order by 7 desc
-- ;
```

## [Analysis] 20251117魚機板更等待時間

```sql
with personal_average as (
  -- 顆粒度:同一user、同一版本、同一機台的平均等待時間 
  select a.*, b.GameName_CHT
  from (
    select UserID, PublishVer, GameID, count(*) as click_counts, avg(waiting_time) as average_waiting_time 
    from (
      select UserID, 
            PublishVer,
            GameID,
            TIMESTAMP_SECONDS(EventTime) AS click_time,
            cast(ClickEventData1 as float64) as waiting_time,  
            row_number() OVER(PARTITION BY UserID, PublishVer, GameID ORDER BY EventTime) as click_order
      from `rd7-data-big-query.bklog.ClickLog`
      where BQDate >= '2025-11-20' and
            UserID not in (select UserID from `rd7-data-big-query.App_Dragon.GameAccount`) and -- 排除公司測試機UserID 
            ClickEventID = 1285 and -- 1285代表點擊魚廳館(任一廳館)
            PublishVer IN ('4.4.1', '4.4.2')
    )
    where click_order != 1
    group by UserID, PublishVer, GameID
  )  as a
  left join `rd7-data-big-query.MobileDW_Dragon.DimGame_ID` as b
    on a.GameID = b.GameID
)

-- 資料顆粒度到版本
select PublishVer, 
       round(avg(average_waiting_time), 3) as avg_waiting_time,
       round(max(median_average_waiting_time), 3) as median_waiting_time, -- any aggregate could apply
       round(stddev(average_waiting_time), 3) as stdev_waiting_time,
       sum(click_counts) as total_click_counts,
from (
  select *, 
         percentile_cont(average_waiting_time, 0.5) over(partition by PublishVer) as median_average_waiting_time
  from personal_average
)
group by PublishVer;



----------------------------分隔線--------------------------------
with personal_average as (
  -- 顆粒度:同一user、同一版本、同一機台的平均等待時間 
  select a.*, b.GameName_CHT
  from (
    select UserID, PublishVer, GameID, count(*) as click_counts, avg(waiting_time) as average_waiting_time 
    from (
      select UserID, 
            PublishVer,
            GameID,
            TIMESTAMP_SECONDS(EventTime) AS click_time,
            cast(ClickEventData1 as float64) as waiting_time,  
            row_number() OVER(PARTITION BY UserID, PublishVer, GameID ORDER BY EventTime) as click_order
      from `rd7-data-big-query.bklog.ClickLog`
      where BQDate >= '2025-11-20' and
            UserID not in (select UserID from `rd7-data-big-query.App_Dragon.GameAccount`) and -- 排除公司測試機UserID 
            ClickEventID = 1285 and -- 1285代表點擊魚廳館(任一廳館)
            PublishVer IN ('4.4.1', '4.4.2')
    )
    where click_order != 1
    group by UserID, PublishVer, GameID
  )  as a
  left join `rd7-data-big-query.MobileDW_Dragon.DimGame_ID` as b
    on a.GameID = b.GameID
)

-- 資料顆粒度到版本和機台
select PublishVer, GameName_CHT,
       round(avg(average_waiting_time), 3) as avg_waiting_time,
       round(max(median_average_waiting_time), 3) as median_waiting_time, -- any aggregate could apply
       round(stddev(average_waiting_time), 3) as stdev_waiting_time,
       sum(click_counts) as total_click_counts,
from (
  select *, 
         percentile_cont(average_waiting_time, 0.5) over(partition by PublishVer, GameName_CHT) as median_average_waiting_time
  from personal_average
)
group by PublishVer, GameName_CHT
order by GameName_CHT, PublishVer;
```

## [Analysis] 新人第二個月BQ作業

```sql
-- 一、(每題4分) 請計算以下日均指標(日期為2025-03，國家為CN)(Hint：請多發問)：
-- 1. DAU/DNU/DOU/回流人數

select round(avg(activeuser), 2) as daily_average_activeuser, 
       round(avg(newuser), 2) as daily_average_newuser,
       round(avg(olduser), 2) as daily_average_olduser,
       round(avg(returnuser), 2) as daily_avg_returnuser
from (
  select BQDate,
        count(UserID) as activeuser,
        sum(case when CreateDate = BQDate then 1 else 0 end) as newuser,
        sum(case when CreateDate != BQDate then 1 else 0 end) as olduser,
        sum(case when CreateDate != BQDate and LastVisitDate is null then 1 else 0 end) as returnuser
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  where BQDate between '2025-03-01' and '2025-03-31' AND
        Country = 'CN'
  group by BQDate
);

-- 2. +1/+3/+7/+14/+30留存率

with march_april_cn_user as (
      select BQDate, UserID
      from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
      where BQDate between '2025-03-01' and '2025-04-30' AND
            Country = 'CN'
), temp_table as (
      select a.*, 
            b.BQDate as active_date,
            date_diff(b.BQDate, a.BQDate, day) as diff_day
      from march_april_cn_user a
      left join march_april_cn_user b
            on a.UserID = b.UserID
      where a.BQDate != b.BQDate
      order by a.BQDate, a.UserID, active_date
), final as (
      select BQDate,
            sum(case when diff_day = 1 then 1 else 0 end) / count(distinct UserID) as oneday_retention,
            sum(case when diff_day = 3 then 1 else 0 end) / count(distinct UserID) as threeday_retention,
            sum(case when diff_day = 7 then 1 else 0 end) / count(distinct UserID) as sevenday_retention,
            sum(case when diff_day = 14 then 1 else 0 end) / count(distinct UserID) as fourteenday_retention,
            sum(case when diff_day = 30 then 1 else 0 end) / count(distinct UserID) as thirtyday_retention,
      from temp_table
      group by BQDate 
)


select round(avg(oneday_retention), 2) as daily_avg_onedayretention,
       round(avg(threeday_retention), 2) as daily_avg_threedayretention,
       round(avg(sevenday_retention), 2) as daily_avg_sevendayretention,
       round(avg(fourteenday_retention), 2) as daily_avg_fourteendayretention,
       round(avg(thirtyday_retention), 2) as daily_avg_thirtydayretention,
from final
where BQDate < '2025-04-01'
;

-- 3. 付費人數 
select round(avg(payer_count),2) as daily_avg_payercount
from (
  select BQDate, count(UserID) as payer_count
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  where BQDate between '2025-03-01' and '2025-03-31' AND
        Country = 'CN' AND
        BuyNumber > 0
  group by BQDate
)
;
-- 4. 付費率
select round(avg(payrate), 2) as daily_avg_payrate
from (
  select BQDate, 
         count(UserID) as alluser, 
         sum(case when BuyNumber > 0 then 1 else 0 end) as payer,
         sum(case when BuyNumber > 0 then 1 else 0 end) / count(UserID) as payrate 
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  where BQDate between '2025-03-01' and '2025-03-31' AND
        Country = 'CN'
  group by BQDate 
)
;
-- 5. 總營收
select round(avg(revenue)) as daily_avg_revenue
from (
  select BQDate, sum(BuyNumber) as revenue
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  where BQDate between '2025-03-01' and '2025-03-31' AND
        Country = 'CN'
  group by BQDate 
)
;

-- 6. ARPPU/ARPU/ARDAU
select round(avg(ARPPU), 2) as daily_avg_arppu,
       round(avg(ARPU), 2) as daily_avg_arpu,
       round(avg(ARDAU), 2) as daily_avg_ardau,
from(
      select BQDate, 
            sum(BuyNumber) / sum(case when BuyNumber > 0 then 1 else 0 end) as ARPPU,
            sum(BuyNumber) / count(*) as ARPU,
            sum(BuyNumber) / count(*) as ARDAU
      from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
      where BQDate between '2025-03-01' and '2025-03-31' AND
            Country = 'CN'
      group by 1
)
;
-- 7. 虎/魚的遊玩人數 
-- 8. 虎/魚的總押量 
-- 9. 虎/魚的總贏量
-- 10. 虎/魚的總押次 
-- 11. 虎/魚的RTP
select round(avg(slot_player_count), 2) as daily_average_slot_player_count, 
       round(avg(fish_player_count), 2) as daily_average_fish_player_count,
       round(avg(total_slot_bet), 2) as daily_average_total_slot_bet,
       round(avg(total_fish_bet), 2) as daily_avg_total_fish_bet,
       round(avg(total_slot_win), 2) as daily_average_total_slot_win, 
       round(avg(total_fish_win), 2) as daily_average_total_fish_win,
       round(avg(total_slot_bettimes), 2) as daily_average_total_slot_bettimes,
       round(avg(total_fish_bettimes), 2) as daily_avg_total_fish_bettimes,
       round(avg(slot_rtp), 2) as daily_average_slot_rtp,
       round(avg(fish_rtp), 2) as daily_avg_fish_rtp,
from (
  select BQDate,
         sum(case when SlotCoinBet != 0 then 1 else 0 end) as slot_player_count,
         sum(case when FishCoinBet != 0 then 1 else 0 end) as fish_player_count,
         sum(SlotCoinBet) as total_slot_bet,
         sum(FishCoinBet) as total_fish_bet,
         sum(SlotCoinWin) as total_slot_win,
         sum(FishCoinWin) as total_fish_win,
         sum(SlotCoinBetTimes) as total_slot_bettimes,
         sum(FishCoinBetTimes) as total_fish_bettimes,
         sum(SlotCoinWin) / sum(SlotCoinBet) as slot_rtp,
         sum(FishCoinWin) / sum(FishCoinBet) as fish_rtp

  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  where BQDate between '2025-03-01' and '2025-03-31' AND
        Country = 'CN'
  group by BQDate
);


-- 12. 虎/魚的SRTP (sessiontigershotbetwinlog, sessionbetwinlog)
select round(avg(srtp), 2) as slot_daily_avg_srtp
from (
      select BQDate,
            sum(totalbet / BetPerSpin) as std_totalbet,
            sum(totalwin / BetPerSpin) as std_totalwin,
            sum(totalwin / BetPerSpin) / sum(totalbet / BetPerSpin) as srtp
      from (
            select BQDate, 
                  BetPerSpin,
                  sum(TotalBet) as totalbet, 
                  sum(TotalWin) as totalwin, 
            from `rd7-data-big-query.bklog.SessionBetWinLog`
            where BQDate between '2025-03-01' and '2025-03-31' AND
                  Country = 'CN' AND
                  BetPerSpin != 0
            group by 1, 2
      )
      group by BQDate
)
;

select round(avg(srtp), 2) as fish_daily_avg_srtp
from (
      select BQDate,
            sum(totalbet / BetPerShoot) as std_totalbet,
            sum(totalwin / BetPerShoot) as std_totalwin,
            sum(totalwin / BetPerShoot) / sum(totalbet / BetPerShoot) as srtp
      from (
            select BQDate, 
                  BetPerShoot,
                  sum(TotalBet) as totalbet, 
                  sum(TotalWin) as totalwin, 
            from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
            where BQDate between '2025-03-01' and '2025-03-31' AND
                  Country = 'CN'
            group by 1, 2
      )
      group by BQDate
)
;

-- 13. 虎/魚的勝率 (totalwins > totalbets的人數除上總遊玩數)
select round(avg(slot_odd), 2) as daily_avg_slotodd,
       round(avg(fish_odd), 2) as daily_avg_fishodd
from (
      select BQDate,
            sum(case when SlotCoinWin > SlotCoinBet then 1 else 0 end) / sum(case when SlotCoinBet > 0 then 1 else 0 end) as slot_odd,
            sum(case when FishCoinWin > FishCoinBet then 1 else 0 end) / sum(case when FishCoinBet > 0 then 1 else 0 end) as fish_odd
      from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
      where BQDate between '2025-03-01' and '2025-03-31' AND
            Country = 'CN'
      group by 1
)
;
-- 14. 一般/黑鑽玩家水位 (水位總和的日均)
select BlackDiamondTag, round(avg(total_endbalance), 2) as daily_avg_toal_endbalance
from (
      select BQDate, BlackDiamondTag, sum(EndBalance) as total_endbalance
      from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
      where BQDate between '2025-03-01' and '2025-03-31' AND
            Country = 'CN'
      group by 1, 2
)
group by 1;


-- 15. 利用金流表計算：平台給予, 遊戲輸贏, 購買獲得, 收贈禮(稅), 平台回收, 淨回收 
select round(avg(freecoin), 2) as daily_avg_freecoin,
       round(avg(betgaincoin), 2) as daily_avg_betgaincoin,
       round(avg(buygaincoin), 2) as daily_avg_buygaincoin,
       round(avg(tax), 2) as daily_avg_tax,
       round(avg(platform_return), 2) as daily_avg_platform_return,
       round(avg(netreturn), 2) as daily_avg_netreturn
from (
      select BQDate, 
            sum(case when Category = '平台給予' then TotalCoinAwarded else 0 end) as freecoin,
            sum(case when Category = '押注回收' then TotalCoinAwarded else 0 end) as betgaincoin,
            sum(case when Category = '購物' then TotalCoinAwarded else 0 end) as buygaincoin,
            sum(case when Category = '價值轉換(贈幣稅)' then TotalCoinAwarded else 0 end) as tax,
            sum(case when Category = '平台回收' then TotalCoinAwarded else 0 end) as platform_return,
            (
            sum(case when Category = '平台給予' then TotalCoinAwarded else 0 end) +
            sum(case when Category = '押注回收' then TotalCoinAwarded else 0 end) +
            sum(case when Category = '價值轉換(贈幣稅)' then TotalCoinAwarded else 0 end) +
            sum(case when Category = '平台回收' then TotalCoinAwarded else 0 end)
            )*(-1) as netreturn
      from `rd7-data-big-query.bklog.SessionCoinLog` a
      left join `rd7-data-big-query.kuochinfu.DataTeamCoinReason` b
            on a.CoinReason = b.CoinReasonId
      where BQDate between '2025-03-01' and '2025-03-31' AND
            UserID in (select distinct UserID 
                              from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot` 
                              where BQDate between '2025-03-01' and '2025-03-31' AND 
                                    Country = 'CN')
      group by BQDate 
)


;
-- 16. 購幣匯率
with date_revenue as (
      select CreateDate, sum(BuyNumber) as buynum
      from `rd7-data-big-query.bklog.GameConsume`
      where CreateDate between 20250301 and 20250331 AND
            Country = 'CN'
      group by 1
), date_coin as (
      select BQDate, sum(TotalCoinAwarded) as buy_coinaward
      from (
            select *
            from `rd7-data-big-query.bklog.SessionCoinLog`
            where BQDate between '2025-03-01' and '2025-03-31' AND
                  UserID in (select distinct UserID 
                             from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot` 
                             where BQDate between '2025-03-01' and '2025-03-31' AND 
                                   Country = 'CN')
            ) a
      left join `rd7-data-big-query.kuochinfu.DataTeamCoinReason` b
            on a.CoinReason = b.CoinReasonId
      where Category = '購物'
      group by 1
), date_exchange_rate as (
      select *, buy_coinaward / buynum as buy_exchange_rate
      from date_revenue a
      left join date_coin b
            on parse_date('%Y%m%d', cast(a.CreateDate as string)) = b.BQDate
)

select round(avg(buy_exchange_rate), 2) as daily_avg_buy_exchange_rate
from date_exchange_rate
; 


-- 17. 一般向黑鑽收量/人數
-- 18. 一般贈黑鑽量/人數
-- 19. 一般向一般收量/人數 
-- 20. 一般贈一般量/人數
select round(avg(received_from_blackdiamond_quantity), 2) as daily_avg_received_from_blackdiamond_quantity,
       round(avg(received_from_blackdiamond_usercounts), 2) as daily_avg_received_from_blackdiamond_usercounts,
       round(avg(sent_to_blackdiamond_quanitty), 2) as daily_avg_sent_to_blackdiamond_quanitty,
       round(avg(sent_to_blackdiamond_usercounts), 2) as daily_avg_sent_to_blackdiamond_usercounts,
       round(avg(received_from_normal_quantity), 2) as daily_avg_received_from_normal_quantity,
       round(avg(received_from_normal_usercounts), 2) as daily_avg_received_from_normal_usercounts,
       round(avg(sent_to_normal_quanitty), 2) as daily_avg_sent_to_normal_quanitty,
       round(avg(sent_to_normal_usercounts), 2) as daily_avg_sent_to_normal_usercounts
from (
      select BQDate,
            sum(CoinReceivedFromBlackDiamond) as received_from_blackdiamond_quantity,
            sum(case when CoinReceivedFromBlackDiamond != 0 then 1 else 0 end) as received_from_blackdiamond_usercounts,
            sum(CoinSentToBlackDiamond) as sent_to_blackdiamond_quanitty,
            sum(case when CoinSentToBlackDiamond != 0 then 1 else 0 end) as sent_to_blackdiamond_usercounts,
            sum(CoinReceivedFromNormal) as received_from_normal_quantity,
            sum(case when CoinReceivedFromNormal != 0 then 1 else 0 end) as received_from_normal_usercounts,
            sum(CoinSentToNormal) as sent_to_normal_quanitty,
            sum(case when CoinSentToNormal != 0 then 1 else 0 end) as sent_to_normal_usercounts
      from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
      where BQDate between '2025-03-01' and '2025-03-31' AND
            Country = 'CN' AND 
            BlackDiamondTag = '一般'
      group by 1
)
;

-- 二、請找出2025-03-01~2025-03-05，CN玩家
-- (5分) 日消費最多的玩家、日(魚+虎)機押量最高的玩家
select BQDate, UserID, 
       buynumber as revenue,
       CoinBet as totalbet
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where BQDate between '2025-03-01' and '2025-03-05' AND
      Country = 'CN'
order by revenue desc
limit 1;

select BQDate, UserID, 
       buynumber as revenue,
       CoinBet as totalbet
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where BQDate between '2025-03-01' and '2025-03-05' AND
      Country = 'CN'
order by totalbet desc
limit 1;

-- (5分) 期間總消費最多的玩家、期間(魚+虎)機總押量最高的玩家
select UserID, 
       sum(buynumber) as revenue,
       sum(CoinBet) as totalbet
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where BQDate between '2025-03-01' and '2025-03-05' AND
      Country = 'CN'
group by 1
order by 2 desc
limit 1;

select UserID, 
       sum(buynumber) as revenue,
       sum(CoinBet) as totalbet
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where BQDate between '2025-03-01' and '2025-03-05' AND
      Country = 'CN'
group by 1
order by 3 desc
limit 1;
-- (10分)找出玩家在此期間單日最高消費金額後，計算消費分組為：
-- 0~100、100~500、500~1000、1000+的人數
-- 並說明如何找出的?
select tag, count(*) as user_counts
from (
      select *,
            case when max_daily_revenue between 0 and 100 then 'under100'
                  when max_daily_revenue between 101 and 500 then 'from101to500'
                  when max_daily_revenue between 501 and 1000 then 'from501to1000'
                  else 'over1000' end as tag
      from (
            select 
                  UserID, 
                  max(buynumber) as max_daily_revenue
            from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
            where BQDate between '2025-03-01' and '2025-03-05' AND
                  Country = 'CN'
            group by 1
      )
)
group by tag
```

## [Analysis] 新上廳館貓拳BP設計

```sql
-- context: 為新廳館貓拳天下設計BP
-- 目的: 快速提升玩家對新廳館的熟悉度 1.至少有玩過的玩家規模 2. 玩過的人是否夠熟悉

-- 查找過去新廳館上線時，前七天的人均日均押注量。以骰子館為例 (ID: 21)
select BQDate, UserID, SUM(TotalBet) as daily_total_bet, sum(TotalBetTimes) as daily_total_bet_times
from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
where BQDate BETWEEN '2025-10-01' and '2025-10-07' and  -- 骰子館於10/1首次上線
      TableTypeID = 21 and
      UserID not in (select UserID from `rd7-data-big-query.App_Dragon.GameAccount`)
group by BQDate, UserID;


select distinct
  percentile_cont(user_daily_average_totalbet, 0)  over() as min_dailybet,
  percentile_cont(user_daily_average_totalbet, 0.25)  over() as first_quantile_dailybet,
  percentile_cont(user_daily_average_totalbet, 0.5)  over() as second_quantile_dailybet,
  percentile_cont(user_daily_average_totalbet, 0.75)  over() as third_quantile_dailybet,
  percentile_cont(user_daily_average_totalbet, 1)  over() as max_dailybet,
from (
  select UserID, round(avg(daily_total_bet)) as user_daily_average_totalbet
  from (
    select BQDate, UserID, SUM(TotalBet) as daily_total_bet, sum(TotalBetTimes) as daily_total_bet_times
    from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
    where BQDate BETWEEN '2025-10-01' and '2025-10-07' and
        TableTypeID = 21 and
        UserID not in (select UserID from `rd7-data-big-query.App_Dragon.GameAccount`) and 
        VipLV >= 3
    group by BQDate, UserID
  )
  group by UserID
)


-- 目的: 找出過往門檻是打指定廳館的BP，並優化其內容當作新廳館BP
-- "2025-11-02#e27c9",	  "2025-11-02#3764d"
-- AE_恐龍_中小客_打底高優惠_v23456_CN, AE_惡靈_中小客_打底高優惠_v23456_CN

-- select a.*, UserTag, UserType
-- from 
--   (select  BatchID, EventName, UserID, VipLV, max(MissionPriority) + 1 as max_completelevel
--     from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
--     where BQDate >= '2025-11-02' and 
--           BatchID in ("2025-11-02#e27c9",	  "2025-11-02#3764d")
--     group by BatchID, EventName, UserID, VipLV
--   ) a
-- left join (select * from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup` where BQDate = '2025-11-01')  b
-- on a.UserID = b.UserID;


-- select distinct UserID, '恐龍' as BoughtBP 
-- from `rd7-data-big-query.bklog.BattlePassBuyLog`
-- where BattlePassID in (select distinct concat('bp_', EventName) from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` where BatchID = "2025-11-02#e27c9")
-- union all
-- select distinct UserID, '惡靈' as BoughtBP 
-- from `rd7-data-big-query.bklog.BattlePassBuyLog`
-- where BattlePassID in (select distinct concat('bp_', EventName) from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` where BatchID = "2025-11-02#3764d")
```

## [BattlePass] 每個玩家的任務完成門檻

```sql
select rl.EventName, mi.MissionBookMark, mi.max_level, MissionPriority + 1 as completed_level, UserID
from (
  select * 
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
  where BQDate >= '2026-02-01'
        AND Country = 'CN'
) rl
inner join (
            select 
                EventName, 
                MissionBookMark,
                count(distinct MissionID) as max_level
            from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
            where BQDate >= '2026-02-01' 
            group by 1, 2
            
            ) mi
  on rl.EventName = mi.EventName
```

## [BattlePass] 任務門檻達成狀況

```sql
with group_usercounts as (
      select NewUserTag, count(*) as TA_usercounts
      from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
      where BQDate = date_trunc(current_date(), month)
            AND Country = 'CN'
      group by 1
), impression_info as (
      select EventName, count(distinct UserID) as impressed_user_counts
      from `rd7-data-big-query.bklog.ActivityMissionPopUpStateLog`
      where BQDate >= date_trunc(current_date(), month)
            AND Country = 'CN'
      group by 1
), mission_info as (
      SELECT 
            *  
      FROM (
      SELECT
            BatchID,
            MissionBookMark,
            eventname,
            -- 使用 SAFE_OFFSET 避免陣列越界錯誤
            SPLIT(MissionBookMark, '_')[SAFE_OFFSET(2)] AS TA_Array,
            MAX(MissionPriority) AS max_level
      FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
      WHERE BQDate between date_trunc(current_date(), month) and current_date()
            AND CountryOperation = 'for'
            AND Country = 'CN'
            AND MissionBookMark NOT LIKE '%公會任務%'
            AND EventName NOT LIKE 'GU%'
            AND MissionBookMark NOT LIKE '奇喵派對內%'
      GROUP BY 1, 2, 3, 4
      ) AS base
      -- 關鍵修正：將 TA 欄位切分後攤平
      CROSS JOIN UNNEST(SPLIT(base.TA_Array, ',')) AS TA_Single
), rewardlog as (
      select EventName, MissionPriority, count(distinct UserID) as engaged_usercounts
      from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
      where BQDate >= date_trunc(current_date(), month)
            AND Country = 'CN'
      group by 1, 2
      order by 1, 2
)


select mi.* except (TA_Array), 
       gu.NewUserTag,
       gu.TA_usercounts, 
       ii.impressed_user_counts, 
       rl.MissionPriority,
       rl.engaged_usercounts,
from mission_info mi
left join group_usercounts gu
      on mi.TA_Single = gu.NewUserTag
left join impression_info ii
      on mi.EventName = ii.EventName
left join rewardlog rl
      on mi.EventName = rl.EventName
order by MissionBookMark, MissionPriority
;

-- declare startdate date default '2026-01-06';
-- declare enddate date default current_date();

-- with complete_log as (
--   select 
--     --distinct 
--             BQDate, 
--             DATETIME(TIMESTAMP_SECONDS(EventTime), "Asia/Taipei") AS CompleteTiming, 
--             UserID, 
--             EventName,
--             MissionPriority + 1 as CompleteLevel
--   from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
--   where BQDate between '2026-01-06' and current_date() AND
--         Country = 'CN'
-- ), user_info as (
--   select BQDate, UserID, NewUserTag, UserTag
--   from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
--   where BQDate between DATE_TRUNC(startdate, MONTH) and DATE_TRUNC(enddate, MONTH) AND
--         Country = 'CN'
-- ), mission_info as (
--   select *
--   from (
--     SELECT *, ROW_NUMBER() OVER(PARTITION BY EventName ORDER BY BatchIDTs DESC) AS recent_rank
--     from (
--       select 
--              distinct 
--               BQDate, 
--               BatchIDTs,
--               BatchID,
--               EventName,
--               PARSE_DATE('%Y%m%d', REGEXP_EXTRACT(EventName, r'_(\d{8})_')) as which_round,
--               MissionPriority,
--               MissionName,
--               MissionBookMark, 
--               ActivityType, 
--               MissionFeature as purpose, 
--               GameCategory as target_metric, 
--       from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--       where BQDate = '2026-01-01' AND -- between '2026-01-01' and '2026-01-02' AND
--             CountryOperation = 'for' AND
--             Country = 'CN'
--     )
--   )
--   where recent_rank = 1
--         AND MissionBookMark NOT LIKE '%公會任務%'  -- 排除包含「公會任務」
--         AND MissionBookMark NOT LIKE '奇喵派對內%' -- 排除開頭為「奇喵派對內」
-- )

-- select a.*, b.NewUserTag, b.UserTag, c.which_round, c.MissionName, c.MissionBookMark, c.ActivityTYpe, c.purpose, c.target_metric
-- from complete_log a
-- left join user_info b
--   on a.UserID = b.UserID
-- left join mission_info c
--   on a.EventName = c.EventName and a.CompleteLevel = c.MissionPriority
-- ;
---

with mission_temp as (
  SELECT MissionBookMark,
         replace(replace(MissionBookMark, '4天', '3天'), '8天', '7天') as MissionBookMark_cleaned,
         max_level, 
         EventName, 
         split(replace(replace(MissionBookMark, '4天', '3天'), '8天', '7天'), '_') as parts
  FROM (
      SELECT 
          *, 
          ROW_NUMBER() OVER(PARTITION BY EventName ORDER BY BatchIDTs DESC) AS recent_rank
      FROM (
          SELECT
              BatchIDTs,
              EventName,
              MissionBookMark,
              MAX(MissionPriority) + 1 as max_level
          FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
          WHERE BQDate BETWEEN '2025-12-01' AND '2025-12-31' 
            AND CountryOperation = 'for' 
            AND Country = 'CN'
            AND MissionBookMark NOT LIKE 'AA%'
            AND MissionBookMark NOT LIKE 'AE%'
            AND MissionBookMark NOT LIKE 'SS%'
          GROUP BY 1,2,3
      )
  )
  WHERE recent_rank = 1 
    AND MissionBookMark NOT LIKE '%公會任務%'  -- 排除包含「公會任務」
    AND EventName NOT LIKE 'GU%'
    AND MissionBookMark NOT LIKE '奇喵派對內%' -- 排除開頭為「奇喵派對內」
), mission_info as ( -- 切分missionbookmark維度、將3日4日和7日8日任務併在一起
  select
    MissionBookMark,
    MissionBookMark_cleaned,
    EventName,
    split(EventName, '_')[offset(4)] as viplevel, 
    max_level,
    parts[SAFE_OFFSET(0)] AS i1,
    parts[SAFE_OFFSET(1)] AS i2,
    -- 手動分類資料未顯示小中大客的MissionBookMark
    case
      when MissionBookMark_cleaned LIKE '淘寶大亨%1天%' then '小客'
      when MissionBookMark_cleaned LIKE '淘寶大亨%3天%' then '中客'
      when MissionBookMark_cleaned LIKE '淘寶大亨%7天%' then '大客'
      when MissionBookMark_cleaned LIKE '兌寶狂歡%1天%' then '小客'
      when MissionBookMark_cleaned LIKE '兌寶狂歡%3天%' then '中客'
      when MissionBookMark_cleaned LIKE '兌寶狂歡%7天%' then '大客'
      when MissionBookMark_cleaned LIKE '節慶活動_收集_0_0_0_%' then '中小客'
      when MissionBookMark_cleaned LIKE '節慶活動_收集%' then '大客'
      when MissionBookMark_cleaned LIKE '節慶活動_活躍%' then '中小客'
      else parts[SAFE_OFFSET(2)]
    end AS customergroup,
    parts[SAFE_OFFSET(3)] AS play_type,
    parts[SAFE_OFFSET(4)] AS machine_fish,
    parts[SAFE_OFFSET(5)] AS runday, 
    -- -- VIP 等級分類邏輯
    -- CASE 
    --   WHEN parts[SAFE_OFFSET(7)] = '1' THEN 'v23456'
    --   WHEN parts[SAFE_OFFSET(7)] = '2' THEN 'v123456'
    --   WHEN parts[SAFE_OFFSET(7)] = '3' THEN 'v6'
    --   WHEN parts[SAFE_OFFSET(7)] = '4' THEN 'v1'
    --   WHEN parts[SAFE_OFFSET(7)] = '5' THEN 'v12'
    --   WHEN parts[SAFE_OFFSET(7)] = '6' THEN 'v456'
    --   WHEN parts[SAFE_OFFSET(7)] = '7' THEN 'v2'
    --   WHEN parts[SAFE_OFFSET(7)] = '8' THEN 'v34'
    --   WHEN parts[SAFE_OFFSET(7)] = '9' THEN 'v56'
    -- END AS viplevel,
    -- 價格分類邏輯
    CASE 
      WHEN parts[SAFE_OFFSET(9)] = '0' THEN '0'
      WHEN parts[SAFE_OFFSET(9)] = '1' THEN '0.99'
      WHEN parts[SAFE_OFFSET(9)] = '2' THEN '1.99'
      WHEN parts[SAFE_OFFSET(9)] = '3' THEN '2.99'
      WHEN parts[SAFE_OFFSET(9)] = '4' THEN '3.99'
      WHEN parts[SAFE_OFFSET(9)] = '5' THEN '5.99'
      WHEN parts[SAFE_OFFSET(9)] = '6' THEN '9.99'
      WHEN parts[SAFE_OFFSET(9)] = '7' THEN '19.99'
      WHEN parts[SAFE_OFFSET(9)] = '8' THEN '29.99'
      WHEN parts[SAFE_OFFSET(9)] = '9' THEN '39.99'
      WHEN parts[SAFE_OFFSET(9)] = '10' THEN '49.99'
      WHEN parts[SAFE_OFFSET(9)] = '11' THEN '59.99'
      WHEN parts[SAFE_OFFSET(9)] = '12' THEN '79.99'
      WHEN parts[SAFE_OFFSET(9)] = '13' THEN '99.99'
      WHEN parts[SAFE_OFFSET(9)] = '14' THEN '199.99'
      WHEN parts[SAFE_OFFSET(9)] = '15' THEN '11.99'
      WHEN parts[SAFE_OFFSET(9)] = '16' THEN '4.99'
      WHEN parts[SAFE_OFFSET(9)] = '17' THEN '149.99'
    END AS price,      
    parts[SAFE_OFFSET(10)] AS note, 
  from mission_temp
), complete_info as ( 
  select EventName, count(distinct UserID) as engaged_usercounts, avg(max_complete_level) as avg_complete_level, max(max_complete_level) as highest_level
  from (
    select EventName, UserID, max(MissionPriority) + 1 as max_complete_level
    from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
    where BQDate between '2025-12-01' AND '2025-12-31'
          AND Country = 'CN'
    group by 1, 2
  )
  group by 1
), impression_info as (
  select EventName, count(distinct UserID) as impressed_usercounts
  from `rd7-data-big-query.bklog.ActivityMissionPopUpStateLog`  -- BP曝光資料，用 曝光人數
  where BQDate between '2025-12-01' and '2025-12-31'
        AND Country = 'CN'
        AND EventName NOT LIKE 'GU%'
  group by EventName
), group_counts as (
    SELECT 
        NewUserTag, 
        COUNT(*) AS target_user_counts,
        -- 定義自定義排序權重
        CASE 
            WHEN NewUserTag = '無客'   THEN 1
            WHEN NewUserTag = '迷你客' THEN 2
            WHEN NewUserTag = '小客'   THEN 3
            WHEN NewUserTag = '中客'   THEN 4
            WHEN NewUserTag = '大客'   THEN 5
            WHEN NewUserTag = '超大客' THEN 6
            ELSE 7
        END AS sort_priority
    FROM `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    WHERE BQDate = '2025-12-01' 
      AND Country = 'CN'
      AND NewUserTag != '負貢獻'
    GROUP BY NewUserTag
), calculated_groupcounts as (
    select NewUserTag, 
           target_user_counts,
           sum(target_user_counts) over(order by sort_priority desc) as cum_target_usercounts
    from group_counts

    union all

    select '中小客' as NewUserTag,
           sum(case when NewUserTag in ('中客', '小客') then target_user_counts else 0 end) as target_user_counts,
           sum(target_user_counts) as cum_target_usercounts
    from group_counts 
    where NewUserTag not in ('無客', '迷你客')
)


select  *, 
        engaged_usercounts / TACounts as target_engagement_ratio,
        engaged_usercounts / impressed_usercounts as abs_engagement_ratio,
        avg_complete_level / max_level as completion_ratio
from (
  select a.*, -- EventName-level
        d.target_user_counts,
        d.cum_target_usercounts,
        c.impressed_usercounts,
        case 
              when customergroup not in ('指定玩家', '指定Tag', '0') then least(c.impressed_usercounts, d.cum_target_usercounts) -- least(a,b): a,b 取小的
              when customergroup = '0' then c.impressed_usercounts
              when customergroup IN ('指定Tag', '指定玩家') then impressed_usercounts
              else -1
        end as TACounts,
        ifnull(b.engaged_usercounts, 0) as engaged_usercounts,
        ifnull(b.avg_complete_level, 0) as avg_complete_level,
        if(b.highest_level = a.max_level, True, False) as any_finish
  from mission_info a
  left join complete_info b
    on a.EventName = b.EventName
  left join impression_info c
    on a.EventName = c.EventName
  left join calculated_groupcounts d
    on a.customergroup = d.NewUserTag
  where impressed_usercounts is not null
)
;




------------------------------------------------------------
-- WITH base_data AS (
--     SELECT DISTINCT 
--         MissionBookMark, 
--         -- 在此處先切分好，並命名為 parts 陣列
--         SPLIT(MissionBookMark, '_') AS parts,
--         EventName,
--         max_level
--     FROM (
--         SELECT 
--             *, 
--             ROW_NUMBER() OVER(PARTITION BY EventName ORDER BY BatchIDTs DESC) AS recent_rank
--         FROM (
--             SELECT 
--                 BatchIDTs,
--                 EventName,
--                 MissionBookMark,
--                 max(MissionPriority) + 1 as max_level
--             FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
--             WHERE BQDate BETWEEN '2026-01-01' AND '2026-01-08' 
--               AND CountryOperation = 'for' 
--               AND Country = 'CN'
--             group by 1, 2, 3
--         )
--     )
--     WHERE recent_rank = 1 
--       AND MissionBookMark NOT LIKE '%公會任務%'  
--       AND MissionBookMark NOT LIKE '奇喵派對內%'
--       AND MissionBookMark NOT IN ('墊底熱門_慶典_指定Tag_惡靈_全_7天_0_1_1_13_收禮解鎖,排9060', '墊底熱門_慶典_指定Tag_惡靈_全_7天_0_1_1_13_收禮解鎖,排商人', '墊底熱門_慶典_指定Tag_獵龍_全_7天_0_1_1_13_收禮解鎖,排9060', '墊底熱門_慶典_指定Tag_獵龍_全_7天_0_1_1_13_收禮解鎖,排商人')
-- )--, mission_info as (
--   SELECT 
--       MissionBookMark,
--       -- 使用 SAFE_OFFSET 存取陣列，避免 Index out of bounds 錯誤
--       parts[SAFE_OFFSET(0)] AS i1,
--       parts[SAFE_OFFSET(1)] AS i2,
--       parts[SAFE_OFFSET(2)] AS customergroup,
--       parts[SAFE_OFFSET(3)] AS play_type,
--       parts[SAFE_OFFSET(4)] AS machine_fish,
--       parts[SAFE_OFFSET(5)] AS runday,
      
--       -- VIP 等級分類邏輯
--       CASE 
--         WHEN parts[SAFE_OFFSET(7)] = '1' THEN 'v23456'
--         WHEN parts[SAFE_OFFSET(7)] = '2' THEN 'v123456'
--         WHEN parts[SAFE_OFFSET(7)] = '3' THEN 'v6'
--         WHEN parts[SAFE_OFFSET(7)] = '4' THEN 'v1'
--         WHEN parts[SAFE_OFFSET(7)] = '5' THEN 'v12'
--         WHEN parts[SAFE_OFFSET(7)] = '6' THEN 'v456'
--         WHEN parts[SAFE_OFFSET(7)] = '7' THEN 'v2'
--         WHEN parts[SAFE_OFFSET(7)] = '8' THEN 'v34'
--         WHEN parts[SAFE_OFFSET(7)] = '9' THEN 'v56'
--       END AS viplevel,
      
--       -- 價格分類邏輯
--       CASE 
--         WHEN parts[SAFE_OFFSET(9)] = '0' THEN '0'
--         WHEN parts[SAFE_OFFSET(9)] = '1' THEN '0.99'
--         WHEN parts[SAFE_OFFSET(9)] = '2' THEN '1.99'
--         WHEN parts[SAFE_OFFSET(9)] = '3' THEN '2.99'
--         WHEN parts[SAFE_OFFSET(9)] = '4' THEN '3.99'
--         WHEN parts[SAFE_OFFSET(9)] = '5' THEN '5.99'
--         WHEN parts[SAFE_OFFSET(9)] = '6' THEN '9.99'
--         WHEN parts[SAFE_OFFSET(9)] = '7' THEN '19.99'
--         WHEN parts[SAFE_OFFSET(9)] = '8' THEN '29.99'
--         WHEN parts[SAFE_OFFSET(9)] = '9' THEN '39.99'
--         WHEN parts[SAFE_OFFSET(9)] = '10' THEN '49.99'
--         WHEN parts[SAFE_OFFSET(9)] = '11' THEN '59.99'
--         WHEN parts[SAFE_OFFSET(9)] = '12' THEN '79.99'
--         WHEN parts[SAFE_OFFSET(9)] = '13' THEN '99.99'
--         WHEN parts[SAFE_OFFSET(9)] = '14' THEN '199.99'
--         WHEN parts[SAFE_OFFSET(9)] = '15' THEN '11.99'
--         WHEN parts[SAFE_OFFSET(9)] = '16' THEN '4.99'
--         WHEN parts[SAFE_OFFSET(9)] = '17' THEN '149.99'
--       END AS price,
      
--       parts[SAFE_OFFSET(10)] AS note,

--       EventName,



--     case
--     -- 手動分類資料未顯示小中大客的MissionBookMark
--       when MissionBookMark LIKE '淘寶大亨%1天%' then '小客'
--       when MissionBookMark LIKE '淘寶大亨%3天%' then '中客'
--       when MissionBookMark LIKE '淘寶大亨%' then '大客'
--       when MissionBookMark LIKE '節慶活動_收集_0_0_0_%天_0_1_1_1_新年' then '中小客'
--       when MissionBookMark LIKE '節慶活動_收集%' then '大客'
--       when MissionBookMark LIKE '節慶活動_活躍%' then '中小客'  
--     -- 手動分類資料有顯示小中大客但不在 MissionBookMark 的客群欄位: 先判斷原先克群欄位是否有值，若無才去查其他欄位
--       when parts[SAFE_OFFSET(2)] not in ('指定Tag', '指定玩家') then parts[SAFE_OFFSET(2)]
--       when MissionBookMark LIKE '大客專屬%' then '大客'
--       when parts[SAFE_OFFSET(10)] LIKE '%大客%' then '大客'
--       when parts[SAFE_OFFSET(10)] LIKE 'ZT' then '大客'
--       else '其他'
--     end as TA
--   FROM base_data
```

## [BattlePass] 查詢上限活動的分布

```sql
SELECT DISTINCT 
    MissionBookMark, 
    purpose, 
    target_metric
FROM (
    SELECT 
        *, 
        ROW_NUMBER() OVER(PARTITION BY EventName ORDER BY BatchIDTs DESC) AS recent_rank
    FROM (
        SELECT 
          DISTINCT
            BatchIDTs,
            EventName,
            MissionBookMark, 
            MissionFeatureCHT AS purpose, 
            GameCategory AS target_metric
        FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        WHERE BQDate BETWEEN '2026-01-01' AND '2026-01-31' 
          AND CountryOperation = 'for' 
          AND Country = 'CN'
    )
)
WHERE recent_rank = 1 
  AND MissionBookMark NOT LIKE '%公會任務%'  -- 排除包含「公會任務」
  AND MissionBookMark NOT LIKE '奇喵派對內%' -- 排除開頭為「奇喵派對內」
  AND target_metric not in ('一般', '銷售型', '儲值活躍人數')
  AND  target_metric NOT LIKE '高返利%'
;





--------------  convert to long format ------------------
WITH base_data AS (
    SELECT DISTINCT 
        MissionBookMark, 
        target_metric,
        -- 在此處先切分好，並命名為 parts 陣列
        SPLIT(MissionBookMark, '_') AS parts
    FROM (
        SELECT 
            *, 
            ROW_NUMBER() OVER(PARTITION BY EventName ORDER BY BatchIDTs DESC) AS recent_rank
        FROM (
            SELECT 
                DISTINCT
                BatchIDTs,
                EventName,
                MissionBookMark, 
                GameCategory AS target_metric
            FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
            WHERE BQDate BETWEEN '2026-01-01' AND '2026-01-31' 
              AND CountryOperation = 'for' 
              AND Country = 'CN'
        )
    )
    WHERE recent_rank = 1 
      AND MissionBookMark NOT LIKE '%公會任務%'  
      AND MissionBookMark NOT LIKE '奇喵派對內%'
      AND MissionBookMark NOT IN ('墊底熱門_慶典_指定Tag_惡靈_全_7天_0_1_1_13_收禮解鎖,排9060', '墊底熱門_慶典_指定Tag_惡靈_全_7天_0_1_1_13_收禮解鎖,排商人', '墊底熱門_慶典_指定Tag_獵龍_全_7天_0_1_1_13_收禮解鎖,排9060', '墊底熱門_慶典_指定Tag_獵龍_全_7天_0_1_1_13_收禮解鎖,排商人')
      AND target_metric NOT IN ('一般', '銷售型', '儲值活躍人數')
      AND target_metric NOT LIKE '高返利%' 
), semi_data as (
  SELECT 
      MissionBookMark,
      -- 使用 SAFE_OFFSET 存取陣列，避免 Index out of bounds 錯誤
      parts[SAFE_OFFSET(0)] AS i1,
      parts[SAFE_OFFSET(1)] AS i2,
      parts[SAFE_OFFSET(2)] AS customergroup,
      parts[SAFE_OFFSET(3)] AS play_type,
      parts[SAFE_OFFSET(4)] AS machine_fish,
      parts[SAFE_OFFSET(5)] AS runday,
      
      -- VIP 等級分類邏輯
      CASE 
        WHEN parts[SAFE_OFFSET(7)] = '1' THEN 'v23456'
        WHEN parts[SAFE_OFFSET(7)] = '2' THEN 'v123456'
        WHEN parts[SAFE_OFFSET(7)] = '3' THEN 'v6'
        WHEN parts[SAFE_OFFSET(7)] = '4' THEN 'v1'
        WHEN parts[SAFE_OFFSET(7)] = '5' THEN 'v12'
        WHEN parts[SAFE_OFFSET(7)] = '6' THEN 'v456'
        WHEN parts[SAFE_OFFSET(7)] = '7' THEN 'v2'
        WHEN parts[SAFE_OFFSET(7)] = '8' THEN 'v34'
        WHEN parts[SAFE_OFFSET(7)] = '9' THEN 'v56'
      END AS viplevel,
      
      -- 價格分類邏輯
      CASE 
        WHEN parts[SAFE_OFFSET(9)] = '0' THEN '0'
        WHEN parts[SAFE_OFFSET(9)] = '1' THEN '0.99'
        WHEN parts[SAFE_OFFSET(9)] = '2' THEN '1.99'
        WHEN parts[SAFE_OFFSET(9)] = '3' THEN '2.99'
        WHEN parts[SAFE_OFFSET(9)] = '4' THEN '3.99'
        WHEN parts[SAFE_OFFSET(9)] = '5' THEN '5.99'
        WHEN parts[SAFE_OFFSET(9)] = '6' THEN '9.99'
        WHEN parts[SAFE_OFFSET(9)] = '7' THEN '19.99'
        WHEN parts[SAFE_OFFSET(9)] = '8' THEN '29.99'
        WHEN parts[SAFE_OFFSET(9)] = '9' THEN '39.99'
        WHEN parts[SAFE_OFFSET(9)] = '10' THEN '49.99'
        WHEN parts[SAFE_OFFSET(9)] = '11' THEN '59.99'
        WHEN parts[SAFE_OFFSET(9)] = '12' THEN '79.99'
        WHEN parts[SAFE_OFFSET(9)] = '13' THEN '99.99'
        WHEN parts[SAFE_OFFSET(9)] = '14' THEN '199.99'
        WHEN parts[SAFE_OFFSET(9)] = '15' THEN '11.99'
        WHEN parts[SAFE_OFFSET(9)] = '16' THEN '4.99'
        WHEN parts[SAFE_OFFSET(9)] = '17' THEN '149.99'
      END AS price,
      
      parts[SAFE_OFFSET(10)] AS note,
      
      -- 指標分類邏輯
      CASE 
        WHEN split_target_metric IN ('收禮人數', '人均收禮量') THEN '社交'
        WHEN split_target_metric IN ('ARPPU', '付費率') THEN '營收'
        WHEN split_target_metric IN ('押量') THEN '深度'
        WHEN split_target_metric IN ('登入活躍人數', '遊玩活躍人數') THEN '活躍'
        ELSE '其他' 
      END AS purpose, 
      
      split_target_metric AS target_metric 

  FROM base_data,
  -- 先處理標點符號統一，再拆分 target_metric 展開成多列
  UNNEST(SPLIT(REPLACE(target_metric, '、', ','), ',')) AS split_target_metric
)

select *,
  case

    -- 手動分類資料未顯示小中大客的MissionBookMark
    when MissionBookMark LIKE '淘寶大亨%1天%' then '小客'
    when MissionBookMark LIKE '淘寶大亨%3天%' then '中客'
    when MissionBookMark LIKE '淘寶大亨%' then '大客'
    when MissionBookMark LIKE '節慶活動_收集_0_0_0_%天_0_1_1_1_新年' then '中小客'
    when MissionBookMark LIKE '節慶活動_收集%' then '大客'
    when MissionBookMark LIKE '節慶活動_活躍%' then '中小客'
    
    -- 手動分類資料有顯示小中大客但不在 MissionBookMark 的客群欄位: 先判斷原先克群欄位是否有值，若無才去查其他欄位
    when customergroup not in ('指定Tag', '指定玩家') then customergroup
    when MissionBookMark LIKE '大客專屬%' then '大客'
    when note LIKE '%大客%' then '大客'
    when note LIKE 'ZT' then '大客'
    else '其他'
  end as TA

from semi_data
```

## [BetStatus] 客群押量十分位數

```sql
-- 虎機單日押注四分位數的平均
with raw as (
  select *,
        percentile_cont(totalbet, 0) over(partition by BQDate, NewUserTag) as minbet,
        percentile_cont(totalbet, 0.25) over(partition by BQDate, NewUserTag) as first_quantile,
        percentile_cont(totalbet, 0.5) over(partition by BQDate, NewUserTag) as second_quantile,
        percentile_cont(totalbet, 0.75) over(partition by BQDate, NewUserTag) as third_quantile,
        percentile_cont(totalbet, 1) over(partition by BQDate, NewUserTag) as maxbet,
        percentile_cont(totalbet, 0.1) over(partition by BQDate, NewUserTag) as ten_percentile,
        percentile_cont(totalbet, 0.2) over(partition by BQDate, NewUserTag) as twenty_percentile,
        percentile_cont(totalbet, 0.3) over(partition by BQDate, NewUserTag) as thirty_percentile,
        percentile_cont(totalbet, 0.4) over(partition by BQDate, NewUserTag) as fourty_percentile,
        percentile_cont(totalbet, 0.6) over(partition by BQDate, NewUserTag) as sixty_percentile,
        percentile_cont(totalbet, 0.7) over(partition by BQDate, NewUserTag) as seventy_percentile,
        percentile_cont(totalbet, 0.8) over(partition by BQDate, NewUserTag) as eighty_percentile,
        percentile_cont(totalbet, 0.9) over(partition by BQDate, NewUserTag) as ninty_percentile
  from (
    select a.BQDate, a.UserID, b.NewUserTag, sum(a.TotalBet) as totalbet
    from (
      select *
      from `rd7-data-big-query.bklog.SessionBetWinLog`
      where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) and Country = 'CN' and TotalBet > 0
    ) a
    inner join 
      (
        select UserID, NewUserTag
        from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
        where BQDate = DATE_TRUNC(CURRENT_DATE(), MONTH) and 
              Country = 'CN' 
      ) b
      on a.UserID = b.UserID
    group by 1, 2, 3
  )
)

select NewUserTag,
       avg(minbet) as avg_minbet, 
       avg(first_quantile) as avg_firtq,
       avg(second_quantile) as avg_secq,
       avg(third_quantile) as avg_thirdq,
       avg(maxbet) as avg_maxbet,
       avg(ten_percentile) as avg_tenp,
       avg(twenty_percentile) as avg_twentyp,
       avg(thirty_percentile) as avg_thirtyp,
       avg(fourty_percentile) as avg_fourtyp,
       avg(sixty_percentile) as avg_sixtyp,
       avg(seventy_percentile) as avg_seventyp,
       avg(eighty_percentile) as avg_eightyp,
       avg(ninty_percentile) as avg_nintyp
from (
  select 
    distinct 
      BQDate, 
      NewUserTag, 
      minbet, 
      first_quantile, 
      second_quantile, 
      third_quantile,
      maxbet,
      ten_percentile,
      twenty_percentile,
      thirty_percentile,
      fourty_percentile,
      sixty_percentile,
      seventy_percentile,
      eighty_percentile,
      ninty_percentile
  from raw
)
group by NewUserTag; 

-- 魚機單日押注四分位數的平均
with raw as (
  select *,
        percentile_cont(totalbet, 0) over(partition by BQDate, NewUserTag) as minbet,
        percentile_cont(totalbet, 0.25) over(partition by BQDate, NewUserTag) as first_quantile,
        percentile_cont(totalbet, 0.5) over(partition by BQDate, NewUserTag) as second_quantile,
        percentile_cont(totalbet, 0.75) over(partition by BQDate, NewUserTag) as third_quantile,
        percentile_cont(totalbet, 1) over(partition by BQDate, NewUserTag) as maxbet,
        percentile_cont(totalbet, 0.1) over(partition by BQDate, NewUserTag) as ten_percentile,
        percentile_cont(totalbet, 0.2) over(partition by BQDate, NewUserTag) as twenty_percentile,
        percentile_cont(totalbet, 0.3) over(partition by BQDate, NewUserTag) as thirty_percentile,
        percentile_cont(totalbet, 0.4) over(partition by BQDate, NewUserTag) as fourty_percentile,
        percentile_cont(totalbet, 0.6) over(partition by BQDate, NewUserTag) as sixty_percentile,
        percentile_cont(totalbet, 0.7) over(partition by BQDate, NewUserTag) as seventy_percentile,
        percentile_cont(totalbet, 0.8) over(partition by BQDate, NewUserTag) as eighty_percentile,
        percentile_cont(totalbet, 0.9) over(partition by BQDate, NewUserTag) as ninty_percentile
        
  from (
    select a.BQDate, a.UserID, b.NewUserTag, sum(a.TotalBet) as totalbet
    from (
      select *
      from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
      where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) and Country = 'CN' and TotalBet > 0
    ) a
    inner join 
      (
        select UserID, NewUserTag
        from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
        where BQDate = DATE_TRUNC(CURRENT_DATE(), MONTH) and 
              Country = 'CN' 
      ) b
      on a.UserID = b.UserID
  group by 1, 2, 3
  )
)

select NewUserTag,
       avg(minbet) as avg_minbet, 
       avg(first_quantile) as avg_firtq,
       avg(second_quantile) as avg_secq,
       avg(third_quantile) as avg_thirdq,
       avg(maxbet) as avg_maxbet,
       avg(ten_percentile) as avg_tenp,
       avg(twenty_percentile) as avg_twentyp,
       avg(thirty_percentile) as avg_thirtyp,
       avg(fourty_percentile) as avg_fourtyp,
       avg(sixty_percentile) as avg_sixtyp,
       avg(seventy_percentile) as avg_seventyp,
       avg(eighty_percentile) as avg_eightyp,
       avg(ninty_percentile) as avg_nintyp
from (
  select 
    distinct 
      BQDate, 
      NewUserTag, 
      minbet, 
      first_quantile, 
      second_quantile, 
      third_quantile,
      maxbet,
      ten_percentile,
      twenty_percentile,
      thirty_percentile,
      fourty_percentile,
      sixty_percentile,
      seventy_percentile,
      eighty_percentile,
      ninty_percentile
  from raw
)
group by NewUserTag; 






-- -- 所有單日綜合的四分位數
-- with raw as (
--   select *,
--         percentile_cont(totalbet, 0) over(partition by NewUserTag) as minbet,
--         percentile_cont(totalbet, 0.25) over(partition by NewUserTag) as first_quantile,
--         percentile_cont(totalbet, 0.5) over(partition by NewUserTag) as second_quantile,
--         percentile_cont(totalbet, 0.5) over(partition by NewUserTag) as third_quantile,
--         percentile_cont(totalbet, 1) over(partition by NewUserTag) as maxbet
--   from (
--     select a.BQDate, a.UserID, b.NewUserTag, sum(a.TotalBet) as totalbet
--     from (
--       select *
--       from `rd7-data-big-query.bklog.SessionBetWinLog`
--       where BQDate >= '2025-12-01' and Country = 'CN' and TotalBet > 0
--     ) a
--     inner join 
--       (
--         select UserID, NewUserTag
--         from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
--         where BQDate = '2025-12-01' and 
--               Country = 'CN' and 
--               NewUserTag NOT IN ('負貢獻', '無客')
--       ) b
--       on a.UserID = b.UserID
--   group by 1, 2, 3
--   )
-- )

-- select distinct NewUserTag, minbet, first_quantile, second_quantile, third_quantile, maxbet
-- from raw
-- ;
```

## [Others] 各客群連續登入天數

```sql
WITH login_rank AS (
  SELECT
    UserID,
    BQDate as login_date,
    ROW_NUMBER() OVER (
      PARTITION BY UserID
      ORDER BY BQDate
    ) AS rn
  FROM `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  WHERE BQDate between '2025-12-01' and '2025-12-31'
        AND Country = 'CN'
)

, streak_group AS (
  SELECT
    UserID,
    login_date,
    DATE_SUB(login_date, INTERVAL rn DAY) AS grp
  FROM login_rank
)


, user_streak AS (
  SELECT
    UserID,
    COUNT(*) AS streak_days
  FROM streak_group
  GROUP BY UserID, grp
)


, user_streak_split AS (
  SELECT
    UserID,
    CASE
      WHEN streak_days >= 7 THEN
        CASE
          WHEN seq < CEIL(streak_days / 7) THEN 7
          ELSE MOD(streak_days, 7)
        END
      ELSE streak_days
    END AS streak_days
  FROM user_streak,
  UNNEST(GENERATE_ARRAY(1, CEIL(streak_days / 7))) AS seq
)




, user_tag as (
  select 
    UserID, 
    NewUserTag
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  where BQDate = '2025-12-01'
        AND Country = 'CN'
)



select NewUserTag, avg(ust.streak_days) as avg_streak_days
from user_streak_split ust
left join user_tag ut
  on ust.UserID = ut.UserID
group by NewUserTag
```

## [Others] 客群常購金額

```sql
declare target_country string default 'JP'; -- 填入國家

with battlepass_buy as (
      select * except(BQDate), extract(month from BQDate) as month
      from `rd7-data-big-query.bklog.BattlePassBuyLog`
      where BQDate >= '2025-11-01'
            AND Country = target_country
), UserTag as (
    select extract(month from BQDate) as month, UserID, NewUserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate >= '2025-11-01'
          AND  Country = target_country
), buylog_with_tag as (
      select a.*, b.NewUserTag
      from battlepass_buy a 
      left join UserTag b
            on a.month = b.month and a.UserID =b.UserID
)


select month, NewUserTag, BuyNumber, count(distinct UserID) as user_counts, count(*) as order_counts
from buylog_with_tag
group by 1, 2, 3
order by 1 desc, NewUserTag desc, BuyNumber desc
```

## [Others] 用營收貢獻算虎機大客超大客

```sql
declare first_day_of_month date default DATE_TRUNC(CURRENT_DATE(), MONTH);

-- with dec_whale_dolphin as (
--       select UserID
--       from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
--       where BQDate = first_day_of_month and 
--             NewUserTag in ('大客', '超大客')
-- )
-- select UserID, 
--        sum(SlotCoinBet) as slot_totalbet,
--        sum(FishCoinBet) as fish_totalbet,
--        safe_divide(sum(SlotCoinBet), sum(FishCoinBet)) as slot2fish_ratio,
--        case when sum(SlotCoinBet) > sum(FishCoinBet) then 1 else 0 end as slot_player
-- from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
-- where BQDate >= first_day_of_month and 
--       UserID in (select UserID from dec_whale_dolphin)
-- group by UserID

-- ;

select UserID, 
      sum(BuyNumber) + sum(TotalCoinReceived)/4000000 - sum(TotalCoinSent) / 4000000 as contribution,
      case when sum(SlotCoinBet) > sum(FishCoinBet) then 1 else 0 end as slot_player
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
where BQDate >= first_day_of_month and Country = 'CN'
group by UserID
having sum(BuyNumber) + sum(TotalCoinReceived)/4000000 - sum(TotalCoinSent) / 4000000 >= 500*31
```

## [Rank] 排行榜結算
**描述：** 節慶任務周排行榜加月排行榜結算用

```sql
declare event_id string default 'AR1767175528'; -- 輸入排行榜id
declare rank_startdate date default '2026-01-01'; -- 輸入排行榜起始日
declare rank_enddate date default '2026-01-30';  -- 輸入排行榜結束日

-- 查看排行榜結果
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = date_add(rank_enddate, interval 1 day) and EventID = event_id
order by Rank
;

-- 查看玩家實際領取的每周token (真正的周排行榜排名)
select UserID, sum(TotalItemAwarded) as total_token
from `rd7-data-big-query.bklog.SessionItemLog`
where BQDate between rank_startdate and rank_enddate
      AND ItemType = 92153 -- 當月tokenB的token id
group by UserID
having sum(TotalItemAwarded) >= 100
order by total_token desc
;


-- 查看領到高優惠禮包特權token的玩家
select *
from `rd7-data-big-query.bklog.SessionItemLog`
where BQDate > rank_enddate 
      AND ItemType = 92188 -- 高優惠禮包token id
;

-- 查看玩家實際領取月積分數量 (真正的月排行榜排名)
select UserID, sum(TotalItemAwarded) as total_token
from `rd7-data-big-query.bklog.SessionItemLog`
where BQDate between '2026-01-01' and '2026-01-29'
      AND ItemType = 92190 -- 月積分token id
group by UserID
order by total_token desc
;


-- select distinct BQDate
-- from `rd7-data-big-query.bklog.BQRankSourceLog`
-- where BQDAte >= '2025-12-01' and ItemType = 92085
```

## [Rank] 熱門機台-排行榜機台挑選
**描述：** 虎機顆粒度: GameID + NewUserTag
魚機顆粒度: BQDate + UserID + Tabletype + FishID + Status

```sql
-- DECLARE target_tags ARRAY<STRING> DEFAULT ['大客', '超大客'];
-- DECLARE target_tags ARRAY<STRING> DEFAULT ['中客', '小客'] ;
-- DECLARE target_tags ARRAY<STRING> DEFAULT ['迷你客', '無客', '負貢獻'] ;
-- DECLARE target_user INT DEFAUILT 104578599 --ZT UserID

-- 全客的熱門虎機台
with bet_log as (
  select *  
  from `rd7-data-big-query.bklog.SessionBetWinLog`
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) AND
        Country = 'CN' AND
        TotalBet > 0
), game_info as (
  select GameID, GameName_CHT
  from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID`
)

select extract(month from BQDate) as month, GameName_CHT, count(distinct UserID) as user_counts, sum(TotalBet) as totalbet
from bet_log
inner join game_info
  using (GameID)
group by extract(month from BQDate), GameName_CHT
order by 2, 1
;

-- 指定客群的熱門虎機台
with bet_log as (
  select *  
  from `rd7-data-big-query.bklog.SessionBetWinLog`
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) and
        TotalBet != 0 AND
        Country = 'CN'
), game_info as (
  select GameID, GameName_CHT
  from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID`
), user_info as (
  select UserID, NewUserTag
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  where BQDate = DATE_TRUNC(CURRENT_DATE(), MONTH)
)

select 
       extract(MONTH FROM a.BQDate) as bet_month,
       c.NewUserTag,
       b.GameName_CHT,
       count(distinct UserID) as user_counts,
       sum(a.TotalBet) as totalbet
from bet_log a
inner join game_info b
  using (GameID)
inner join user_info c
  using (UserID)
-- where NewUserTag in unnest( target_tags)
group by 1, 2, 3
;



-- 全客的熱門魚機台
with bet_log as (
  select *  
  from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) 
        AND Country = 'CN'
        AND TotalBet > 0
), tabletype_info as (
  select TableTypeIDKey, TableTypeIDName_TW
  from `rd7-data-big-query.MobileDW_Dragon.DimTableTypeID`
)

select extract(month from BQDate) as month, 
       TableTypeIDName_TW, 
       sum(TotalBet) as totalbet, 
       count(distinct UserID) as user_counts
from bet_log a
inner join tabletype_info b
  on a.TableTypeID = b.TableTypeIDKey
group by extract(month from BQDate), TableTypeIDName_TW
order by 2, 1
;

-- 指定客群的熱門魚機台
with bet_log as (
  select *  
  from `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) 
        AND TotalBet != 0 
        AND Country = 'CN'
), tabletype_info as (
  select TableTypeIDKey, TableTypeIDName_TW
  from `rd7-data-big-query.MobileDW_Dragon.DimTableTypeID`
), user_info as (
  select UserID, NewUserTag
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  where BQDate = DATE_TRUNC(CURRENT_DATE(), MONTH) 
)

select 
       extract(MONTH FROM a.BQDate) as bet_month,
       c.NewUserTag,
       b.TableTypeIDName_TW,
       count(distinct UserID) as user_counts,
       sum(a.TotalBet) as totalbet
from bet_log a
inner join tabletype_info b
  on a.TableTypeID = b.TableTypeIDKey
inner join user_info c
  using (UserID)
-- where NewUserTag in unnest(target_tags)
group by 1, 2, 3
;


-- 熱門魚種挑選
with bet_log as (
  select *
  FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
  INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
    ON a.UserID = b.user_id
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH) 
        
), fish_info as (
  select FishID, FishName_CHT
  from `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds`
)

select a.FishID, Status, b.FishName_CHT, sum(TotalBet) as TotalBet, sum(TotalWin) as TotalWin
from bet_log a
left join fish_info b
  on a.FishID = b.FishID
group by 1, 2, 3
order by 4 desc
;





-- 目的: 阿茲特克、猴爺魚排行榜參與低下
select *, TotalBet / 31 as daily_totalbet -- 一月熱門魚種
from(
      select FishID, Status,  sum(TotalBet) as TotalBet, sum(TotalWin) as TotalWin
      FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
      INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
            ON a.UserID = b.user_id
      where BQDate between '2026-01-01' and '2026-01-31'
            AND BetPerShoot >= 100000
      group by 1, 2
) a
left join (
            select FishID, FishName_CHT
            from `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds`
            ) b
      on a.FishID = b.FishID
order by a.TotalBet desc
;

select b.GameName_CHT, 
      sum(TotalBet) as totalbet, 
      sum(TotalWIn) as totalwin,
      sum(TotalBet) / 31 as daily_totalbet -- 一月熱門機台
from (
      select *
      from `rd7-data-big-query.bklog.SessionBetWinLog`
      where BQDate between '2026-01-01' and '2026-01-31'
            AND Country = 'CN'
            AND BetPerSpin >= 1000000
) a
left join (
            select GameID, GameName_CHT
            from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID`
            ) b
      on a.GameID = b.GameID
group by 1
order by 2 desc
;

-- Step 1: 確認事實(真的低嗎?排行榜資料庫問題?)
SELECT
  a.UserID,
  SUM(a.TotalBet) AS TotalBet,
  SUM(a.TotalWin) as TotalWin
FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
  ON a.UserID = b.user_id
WHERE a.BQDate between '2026-02-02' and '2026-02-03'
  AND a.TableTypeID IN (12, 13, 14) -- VIP三個廳館
  AND a.FishID = 116 -- 猴爺魚
  AND a.BetPerShoot >= 100000
GROUP BY a.UserID
ORDER BY 3 DESC
; 

SELECT
  a.UserID,
  SUM(a.TotalBet) AS TotalBet,
  SUM(a.TotalWin) as TotalWin
FROM `rd7-data-big-query.bklog.SessionBetWinLog` a
WHERE a.BQDate between '2026-02-02' and '2026-02-03'
      AND Country = 'CN'
      AND a.GameID = 509 -- 阿茲特克
      -- AND a.BetPerSpin >= 1000000
GROUP BY a.UserID
HAVING sum(a.TotalWin) >= 3138500
ORDER BY 3 DESC
;

-- Step 2: 排查問題，主要玩家玩的情況如何
 -- aztec_player
select UserID, 
      sum(TotalBet) as totalbet, 
      sum(TotalBet) / 31 as daily_totalbet
from `rd7-data-big-query.bklog.SessionBetWinLog`
where BQDate between '2026-01-01' and '2026-01-31'
      AND Country = 'CN'
      AND BetPerSpin >= 1000000
      AND GameID = 509
group by 1
order by 2 desc
;

-- hoyeahfish_hunter: 看一月玩家，單日押量狀況
SELECT
  a.BQDate,
  a.UserID,
  SUM(a.TotalBet) AS TotalBet
FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
  ON a.UserID = b.user_id
WHERE a.BQDate between '2026-01-01' and '2026-01-31'
  AND a.TableTypeID IN (12, 13, 14)
  AND a.FishID = 116 -- 猴爺魚
  AND a.BetPerShoot >= 100000
GROUP BY 1, 2
ORDER BY 3 DESC
; 


-- 一月Aztec總押量前百名玩家，有幾位有參加排行榜
select count(distinct UserID)
from `rd7-data-big-query.bklog.SessionActive`
where BQDate = '2026-02-02'
      AND Country = 'CN'
      AND UserID in 
                    ( 
                      select UserID
                      from 
                        (
                        select UserID, sum(TotalBet) 
                        from `rd7-data-big-query.bklog.SessionBetWinLog`
                        where BQDate between '2026-01-01' and '2026-01-31'
                            AND Country = 'CN'
                            AND BetPerSpin >= 1000000
                            AND GameID = 509
                        group by 1
                        order by 2 desc
                        )
                      limit 100
                    )
```

## [Social] 收贈幣量四分位數

```sql
-- transaction-level: 遊戲贈禮面額限制導致當玩家買25M時，會被記錄成兩筆12.5M。應該要再分玩家單日收禮量

select NewUserTag, count(distinct a.ReceiverID) as usercounts, APPROX_QUANTILES(ReceiverCoinAward, 4) AS receivedcoin_quartiles 
from (
  select *
  from `rd7-data-big-query.bklog.GemToCoinGiftAwardLog`
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH)
) a
inner join (select  * from `rd7-data-big-query.kuochinfu.watchlist` where GroupID = 1 and Country = 'CN') b
  on a.SenderID = b.UserID
left join 
      (
        select UserID, NewUserTag
        from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
        where BQDate = DATE_TRUNC(CURRENT_DATE(), MONTH) and 
              Country = 'CN' 
      )  c
  on a.ReceiverID = c.UserID
group by 1
;
--
select NewUserTag, count(distinct a.ReceiverID) as usercounts, APPROX_QUANTILES(ReceiverCoinAward, 4) AS receivedcoin_quartiles 
from (
  select *
  from `rd7-data-big-query.bklog.GemToCoinGiftAwardLog`
  where BQDate >= DATE_TRUNC(CURRENT_DATE(), MONTH)
        AND ReceiverCoinAward > 0
) a
inner join (select  * from `rd7-data-big-query.kuochinfu.watchlist` where GroupID = 1 and Country = 'CN') b
  on a.SenderID = b.UserID
left join 
      (
        select UserID, NewUserTag
        from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
        where BQDate between '2025-12-01' and '2025-12-31' 
              AND Country = 'CN' 
      )  c
  on a.ReceiverID = c.UserID
group by 1
```

## [Rank] 驗證魚種排行榜顯示與實際排名
**描述：** 改startdate, endate, gameId 

```sql
SELECT
  a.UserID,
  SUM(a.TotalBet) AS TotalBet,
  SUM(a.TotalWin) as TotalWin
FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
  ON a.UserID = b.user_id
WHERE a.BQDate between '2026-02-05' and '2026-02-11'
  AND a.FishID = 244 -- 龍舞極
  AND a.BetPerShoot >= 100000
GROUP BY a.UserID
ORDER BY 3 DESC
;
```

## [Rank] 排行榜設計控RTP
**描述：** 改GameID 來看要出的機台過往押量狀況，判斷獎勵要放啥跟幾天

```sql
-- 排行榜設計: 前三名控10%、整體控5%

select BQDate, UserID, sum(TotalBet) as totalbet
from `rd7-data-big-query.bklog.SessionBetWinLog`
where BQDate >= '2026-01-01'
  AND Country = 'CN'
  AND GameID = 325
  AND TotalBet > 0
group by 1, 2
order by 3 desc
```

## [Others] 二月刮刮卡BP設計
**描述：** 中客以上在2024二月整月刮刮卡的狀況

```sql
with

  usertag as (
    select BQDate, UserID, NewUserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where (BQDate = '2026-02-01' OR BQDate = '2024-02-01') 
      AND Country = 'CN'
      AND NewUserTag in ('中客', '大客', '超大客')
  )


, scratch as (
  select *, date_trunc(BQDate, Month) as first_date
  from `rd7-data-big-query.preprocessed_bklog.DailyUserGameMetrics`
  where (BQDate >= '2026-02-01' OR BQDate between '2024-02-01' and '2024-02-28')
      AND Country = 'CN'
      AND GID LIKE 'ScratchLottery%'
)


select s.*, u.NewUserTag
from scratch s
inner join usertag u
  on s.first_date = u.BQDate and s.UserID = u.UserID
```

## [Others] 過年擊殺魚掉落道具
**描述：** 估計活動檔期每個人會有多少個token，配五行條件

```sql
with fish_info as (
  select FishID, Status, FishName_CHT,
    case 
      when FishID in (199, 9070) then '錦鯉'
      when FishID in (222, 246) then '春'
      when FishID in (9092, 245) then "招財貓"
    end as token
  from `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds`
  where FishID IN (199, 9070, 222, 246, 9092, 245)
)


, win_log as (
  select UserID, FishID, sum(WinTimes) as win_times  
  from `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog`
  where BQDate between '2026-01-01' and '2026-01-31'
    AND UserID in (select user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN')
    AND FishID IN (199, 9070, 222, 246, 9092, 245)
    AND WinTimes > 0
    AND VipLevel >= 3
  group by 1, 2
  order by 1, 3 desc
)


, semi as (
select w.*, f.FishName_CHT, token,
  case 
    when w.FishID in (199, 222) then floor(win_times * 0.8) * 100
    when w.FishID = 9092 then floor(win_times * 1) * 100
    when w.FishID = 245 then floor(win_times * 0.7264) * 100
    when w.FishID = 246 then floor(win_times * 0.49) * 100
    when w.FishID = 9070 then floor(win_times * 0.304) * 100
  end as expected_gettimes
from win_log  w
left join fish_info f
  on w.FishID = f.FishID
)

select token, 
        count(distinct UserID) as usercounts, 
        sum(expected_gettimes) as total_get, 
        sum(expected_gettimes) / count(distinct UserID) as avg_get,
        ( sum(expected_gettimes) / count(distinct UserID) ) / 7 as pred_get
from semi
group by token
```

## [BetStatus] 抓VIP館每日押量
**描述：** 驗證二月VIP管是否因為福利(原打底高優惠)從VIP館改貓拳導致押量下降

```sql
SELECT 
  day, 
  -- 1. 先用 CASE 分配資料，再用 MAX 壓縮列
  MAX(CASE WHEN month = 1 THEN user_counts END) AS jan_usercounts,
  MAX(CASE WHEN month = 2 THEN user_counts END) AS feb_usercounts,
  MAX(CASE WHEN month = 1 THEN total_bet / 1000000 END) AS jan_total_bet_M,
  MAX(CASE WHEN month = 2 THEN total_bet / 1000000 END) AS feb_total_bet_M
FROM (
  SELECT 
    EXTRACT(MONTH FROM BQDate) AS month, 
    EXTRACT(DAY FROM BQDate) AS day,
    COUNT(DISTINCT UserID) AS user_counts, 
    SUM(TotalBet) AS total_bet
  FROM `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
  WHERE (BQDate BETWEEN '2026-02-01' AND '2026-02-09' OR BQDate BETWEEN '2026-01-01' AND '2026-01-09')
    AND Country = 'CN'
    AND TableTypeID IN (12, 13, 14)
  GROUP BY 1, 2
)
GROUP BY day
ORDER BY day
```

## [BetStatus] ZT 押量
**描述：** ZT近兩個月最愛機台跟每日押量

```sql
with game_info as (
  select GameID, GameName_CHT
  from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID`
)
, bet_log as (
  select BQDate, GameID, sum(TotalBet) as totalbet
  from `rd7-data-big-query.bklog.SessionBetWinLog`
  where BQDate >= date_sub( date_trunc(current_date('Asia/Taipei'), month), interval 1 month)  
    AND Country = 'CN'
    AND UserID = 104578599 --ZT UserID
  group by 1, 2
)
, bet_data as (
  select b.*, g.GameName_CHT
  from bet_log b
  left join game_info g
    on b.GameID =g.GameID
  order by totalbet desc
)
, game_betstatus as (
  select GameName_CHT, 
        count(*) as play_days, 
        sum(TotalBet) as total_bet,  
        sum(TotalBet) / count(*) as daily_avg_bet
  from bet_data
  group by GameName_CHT
  order by 4 desc
)

select 
  distinct
       percentile_cont(totalbet, 0) over() as minbet,
       percentile_cont(totalbet, 0.10) over() as bet10,
       percentile_cont(totalbet, 0.20) over() as bet20,
       percentile_cont(totalbet, 0.30) over() as bet30,
       percentile_cont(totalbet, 0.40) over() as bet40,
       percentile_cont(totalbet, 0.50) over() as bet50,
       percentile_cont(totalbet, 0.60) over() as bet60,
       percentile_cont(totalbet, 0.70) over() as bet70,
       percentile_cont(totalbet, 0.80) over() as bet80,
       percentile_cont(totalbet, 0.90) over()  as bet90,
       percentile_cont(totalbet, 1) over() as maxbet,
from bet_data
where GameID = 317
```

## [Others] 2026過年期間排行榜，高優惠禮包特權玩家名單

```sql
-- 0212~0217虎機五日累積排行榜: "AR1770820517"
-- 高優惠禮包資格: Top 20 
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-18' and EventID = "AR1770820517"
order by Rank
limit 20
;

-- 0217~0222虎機五日累積排行榜: "AR1770866201"
-- 高優惠禮包資格: Top 20 
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-23' and EventID = "AR1770866201"
order by Rank
limit 20
;


-- 0222~0227虎機五日累積排行榜: "AR1770866283"
-- 高優惠禮包資格: Top 20 
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-28' and EventID = "AR1770866283"
order by Rank
limit 20
;




-- 0213~0216魚機掉落TokenA錦鯉排行榜:"AR1770875610"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-17' and EventID = "AR1770875610"
order by Rank
limit 5
;
-- 0217~0220魚機掉落TokenA錦鯉排行榜:"AR1770875611"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-21' and EventID = "AR1770875611"
order by Rank
limit 5
;
-- 0221~0224魚機掉落TokenA錦鯉排行榜:"AR1770875612"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-25' and EventID = "AR1770875612"
order by Rank
limit 5
;



-- 0213~0216魚機掉落TokenB春排行榜:"AR1770875730"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-17' and EventID = "AR1770875730"
order by Rank
limit 5
;
-- 0217~0220魚機掉落TokenB春排行榜:"AR1770875731"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-21' and EventID = "AR1770875731"
order by Rank
limit 5
;
-- 0221~0224魚機掉落TokenB春排行榜:"AR1770875732"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-25' and EventID = "AR1770875732"
order by Rank
limit 5
;




-- 0213~0216魚機掉落TokenC招財貓排行榜:"AR1770875818"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-17' and EventID = "AR1770875818"
order by Rank
limit 5
;
-- 0217~0220魚機掉落TokenC招財貓排行榜:"AR1770875819"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-21' and EventID = "AR1770875819"
order by Rank
limit 5
;
-- 0221~0224魚機掉落TokenC招財貓排行榜:"AR1770875820"
-- 高優惠禮包資格: Top 5
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-25' and EventID = "AR1770875820"
order by Rank
limit 5
;



-- 0213~0224魚機三種Token掉落累積排行榜: ""
-- 高優惠禮包資格: Top 20 
select Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate = '2026-02-25' and EventID = ""
order by Rank
limit 20
;
```

## [Analysis] 2026/2加開上古神獸次數任務
**描述：** 刺激上古神獸排行榜，多開次數BP，撈中客以上的玩家們每日的押次分布，取10% - 50%作為任務門檻

```sql
with user_tag as (
  select UserID, NewUserTag
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  where BQDate = '2026-02-01'
    AND Country = 'CN'
    AND NewUserTag in ('中客', '大客', '超大客')
)


, tigergshark_log as (
  select BQDate, UserID, sum(BetTimes) as totalbettimes, sum(TotalBet) as totalbet 
  FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
  INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
    ON a.UserID = b.user_id
  WHERE BQDate >= '2026-02-01' 
    AND FishID = 244
  GROUP BY 1, 2
)


select t.*, 
       u.NewUserTag,
       percentile_cont(totalbettimes, 0.1) over () as ten_p,
       percentile_cont(totalbettimes, 0.3) over () as thirty_p
from tigergshark_log t
inner join user_tag u
  on t.UserID = u.UserID
```

## [Analysis] 2026/02/13客訴
**描述：** 中大客連續登入任務25632221明明都有登但任務紀錄上沒寄到

```sql
-- 客訴: 沒有領到31天的任務

select distinct BQDate
from `rd7-data-big-query.bklog.SessionActive`
where BQDate >= '2026-01-14'
  AND Country = 'CN'
  AND UserID = 25632221
order by BQDate
;


-- select UserID, count(*)
-- from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
-- where BQDate >= '2026-01-14'
--   AND Country = 'CN'
--   AND EventName = 'SP_LV2_20260114_3_v23456_for_cn_G'
-- group by 1
-- ;
```

## [Analysis] 過年期間捕魚掉落物排行榜分析
**描述：** 活動期間 2/13-2/24 以及 活動前 2/ 1 -2/12 六隻魚的押量狀況 (是否有提升)
各排行榜越來越強還是有疲弱趨勢
各個排行榜RTP有沒有爆炸

```sql
-- 過年期間捕魚掉落物排行榜效果

-- 是否提升押量
with fish_info as (
  select FishID, Status, FishName_CHT,
    case 
      when FishID in (199, 9070) then '錦鯉'
      when FishID in (222, 246) then '春'
      when FishID in (9092, 245) then "招財貓"
    end as token
  from `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds`
  where FishID IN (199, 9070, 222, 246, 9092, 245)
)


, bet_log as (
  SELECT
    a.UserID,
    a.FishID,
    case 
      when a.BQDate < '2026-02-13' then 'before'
      when a.BQDate >= '2026-02-13' then 'after'
    end as timing,
    SUM(a.TotalBet) AS TotalBet
  FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
  INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
    ON a.UserID = b.user_id
  WHERE a.BQDate between '2026-02-03' and '2026-02-22'
    AND a.FishID in  (199, 9070, 222, 246, 9092, 245)
  GROUP BY 1, 2, 3
  ORDER BY 1,2 desc
)

select fi.FishName_CHT, 
       fi.token, 
       timing, 
       count(distinct UserID) as usercounts, 
       sum(TotalBet) as totalbet,
       sum(TotalBet) / count(distinct UserID) as avg_bet
from bet_log bl
left join fish_info fi
  on bl.FishID = fi.FishID
group by 1, 2, 3
order by 2, 1, 3 desc
; 


-- 三個檔期間是否越來越弱、RTP是否爆掉
with rank_result as (
  select BQDate,
        case
          when EventID in ('AR1770875610', 'AR1770875611', 'AR1770875612') then '錦鯉'
          when EventID in ('AR1770875730', 'AR1770875731', 'AR1770875732' ) then '春'
          when EventID in ('AR1770875818', 'AR1770875819', 'AR1770875820') then '招財貓'
        end as rank_type,
        EventID, 
        Rank, 
        UserID,
        Score
  from `rd7-data-big-query.bklog.RankSettlementLog`
  where BQDate in ('2026-02-17', '2026-02-21', '2026-02-25')
    AND EventID in (
                    'AR1770875610', 'AR1770875730', 'AR1770875818',
                    'AR1770875611', 'AR1770875731', 'AR1770875819',
                    'AR1770875612', 'AR1770875732', 'AR1770875820'
                  )
  order by rank_type, BQDate, Rank
)

, user_bet as (
  SELECT
    case 
      when a.BQDate between '2026-02-13' and '2026-02-16' then date('2026-02-17')
      when a.BQDate between '2026-02-17' and '2026-02-20' then date('2026-02-21')
      when a.BQDate between '2026-02-21' and '2026-02-24' then date('2026-02-25')
    end as timing,
    a.UserID,
    case 
      when FishID in (199, 9070) then '錦鯉'
      when FishID in (222, 246) then '春'
      when FishID in (9092, 245) then "招財貓"
    end as token,
    SUM(a.TotalBet) AS TotalBet
  FROM `rd7-data-big-query.bklog.TigerSharkFishStatisticsLog` a
  INNER JOIN (select distinct user_id from `rd7-data-big-query.ExtData_Dragon.UserInfo` where ip_country = 'CN') b
    ON a.UserID = b.user_id
  WHERE a.BQDate between '2026-02-13' and '2026-02-22'
    AND a.FishID in  (199, 9070, 222, 246, 9092, 245)
    AND a.UserID in (select distinct UserID from rank_result)
  GROUP BY 1, 2, 3
  ORDER BY 1,2 desc
)

select rr.*, ub.TotalBet
from rank_result rr
left join user_bet ub
  on rr.BQDate = ub.timing and rr.rank_type = ub.token and rr.UserID = ub.UserID
order by rank_type, BQDate, Rank
```

## [Analysis] 過年期間六小時虎機馬拉松排行榜分析
**描述：** 活動期間 2/12 - 2/26 以及活動前的全虎機富豪館押量是否提升 (排行榜是否有效提升押量)
三輪的RTP 有沒有爆炸

```sql
-- 過年期間虎機排行榜效果

-- 是否提升押量: 虎機過年排行榜活動期間
select
      case 
        when BQDate <= '2026-02-11' then 'before'
        when BQDate >= '2026-02-12' then 'after' 
      end as timing,
      sum(TotalBet) as totalbet
from `rd7-data-big-query.bklog.SessionBetWinLog`
where BQDate between '2026-02-01' and '2026-02-22' -- 活動檔期為2/12-2/26
  AND Country = 'CN'
  AND GameID in (select distinct GameID 
                 from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID` 
                 where GameName_CHT like '[高分館]%')
group by 1
order by 1 desc
;
-- 三個檔期間是否越來越弱、RTP是否爆掉
with rank_result as (
  select BQDate,
        EventID, 
        Rank, 
        UserID,
        Score
  from `rd7-data-big-query.bklog.RankSettlementLog`
  where BQDate in ('2026-02-18', '2026-02-23', '2026-02-28')
    AND EventID in (
                    'AR1770820517', 'AR1770866201', 'AR1770866283'
                  )
  order by BQDate, Rank
)

, user_bet as (
  SELECT
    case 
      when a.BQDate between '2026-02-12' and '2026-02-16' then date('2026-02-18')
      when a.BQDate between '2026-02-17' and '2026-02-21' then date('2026-02-23')
      when a.BQDate between '2026-02-22' and '2026-02-26' then date('2026-02-28')
    end as timing,
    a.UserID,
    SUM(a.TotalBet) AS TotalBet
  FROM `rd7-data-big-query.bklog.SessionBetWinLog` a
  WHERE a.BQDate between '2026-02-12' and '2026-02-27'
    AND Country = 'CN'
    AND a.GameID in (select distinct GameID 
                 from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID` 
                 where GameName_CHT like '[高分館]%')
    AND a.UserID in (select distinct UserID from rank_result)
  GROUP BY 1, 2
  ORDER BY 2, 1 
)

select rr.*, ub.TotalBet
from rank_result rr
left join user_bet ub
  on rr.BQDate = ub.timing and rr.UserID = ub.UserID
order by BQDate, Rank
;

-- 過年虎機六小時是否疲弱
select BQDate, 
       EventID, 
       DATETIME(TIMESTAMP_SECONDS(StartTime), 'Asia/Taipei') as startime,
       DATETIME(TIMESTAMP_SECONDS(EndTime), 'Asia/Taipei') as endtime,
       Rank, UserID, Score
from `rd7-data-big-query.bklog.RankSettlementLog`
where BQDate between '2026-02-12' and  '2026-02-27'
  AND EventID in ('AR1770865938', 'AR1770865939', 'AR1770865940', 'AR1770865941', 'AR1770865942', 'AR1770865943', 'AR1770865944', 'AR1770865945', 'AR1770865946', 'AR1770865947', 'AR1770865948', 'AR1770865949', 'AR1770865950', 'AR1770865951', 'AR1770865952', 'AR1770865953', 'AR1770865954', 'AR1770865955', 'AR1770865956', 'AR1770865957')
order by 4, 5
```

## [Others] 計算BP RTP
**描述：** 追蹤任務返利RTP、製作儀錶板

```sql
with mission_info as ( -- 顆粒度到mission_id、整理出計算RTP所需資料(尚未處理上錯的)
  select 
    distinct 
      BQDate, 
      MissionBookMark, 
      split(MissionBookMark, '_')[offset(2)] as target_audience,
      MissionPriority, 
      MissionName, 
      case -- 提取每階的門檻(全轉換成押量，後續計算RTP用)
        -- 魚 
         when Rule = 'fish_shot' or Rule like '%bet_times' then  TargetTimes * if(JSON_VALUE(AppendRule, '$.fish_room') = 'vip' OR lower(split(MissionBookMark, '_')[3]) like  'vip',5000,2000)  
        -- 虎
        when Rule = 'slot_spin' then TargetTimes * coalesce(cast(JSON_VALUE(AppendRule, '$.bet') as int64), 500) 
        when Rule like '%bet' or Rule like '%win' then TargetTimes -- 魚: f_room_fish_bet/win、fish_totalwin/bet、target_fish_win; 虎:slot_totalbet/win 直接是押量門檻
        else -1 
      end as threshold_bet,
      (MissionValue - MissionCardValue) as free_reward_exc_cards,
      (BPMissionValue - BPMissionCardValue) as pay_reward_exc_cards,
      BatchID,
      BatchIDTs,
      -- case
      --   when GameType = 'slot' then ActivityGameID
      --   when GameType = 'fish' then concat(ifnull(JSON_VALUE(AppendRule, '$.fish_name'), 'all') , '_', JSON_VALUE(AppendRule, '$.fish_room'))
      -- end as ActivityGameID,
      case
        when GameType = 'slot' then JSON_VALUE(AppendRule, '$.high_roll')
        when GameType = 'fish' then coalesce(JSON_VALUE(AppendRule, '$.fish_room'), JSON_VALUE(AppendRule, '$.fishroom'), split(JSON_VALUE(AppendRule, '$.target_name'), '_')[offset(0)], split(MissionBookMark, '_')[offset(3)])
      end as HighRoll_FishRoom,
      case
        when GameType = 'slot' then JSON_VALUE(AppendRule, '$.game_id')
        when GameType = 'fish' then coalesce(JSON_VALUE(AppendRule, '$.fish_name'),JSON_VALUE(AppendRule, '$.fishname'), b.FishName,  'all')
      end as Machine_Fish,
      GameType,
      EventName,
      AppendRule
      -- SAFE_CAST(JSON_VALUE(AppendRule, '$.bet') AS INT64) AS bet_numeric
  from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` a
  LEFT JOIN 
    (
    SELECT DISTINCT LOWER(FishName) AS FishName, FishName_CHT
    FROM `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds`
    ) b 
    ON STRPOS(LOWER(a.ActivityGameID), b.FishName) > 0 -- 用來抓每個任務出在哪條魚上
  where BQDate between parse_date('%Y%m%d', @DS_START_DATE) and parse_date('%Y%m%d', @DS_END_DATE)
    AND CountryOperation = 'for'
    AND Country = 'CN'
    AND ActivityType != 'GU'
    AND MissionBookMark not like '奇喵派對內%'
    AND GameType in ('fish', 'slot')
    AND (
        -- 魚: 不限魚種的押注/贏分任務; 虎:只要是押注/贏分任務都算這裡 
        Rule like '%totalbet%' 
        OR Rule like '%totalwin%'
        -- 虎: 次數任務(不論是否有卡bet段)
        OR Rule = 'slot_spin'
        -- 魚: 指定魚種的押注/贏分/次數任務
        Or Rule like 'f_room_fish%' 
        -- 魚: 不限魚種的次數任務
        OR Rule = 'fish_shot' 
        -- target_fish系列 只有惡靈館跟威鯨館
        OR Rule like 'target%'
        )
  -- order by BQDate, MissionBookMark, MissionPriority
)

, deduplicated_eventname as (
  select 
    distinct
      * except(recent_rank, BatchID, BatchIDTs, BQDate, EventName)
  from (
    select *, 
         sum(free_reward_exc_cards) over (partition by  BQDate, BatchID, EventName order by MissionPriority) as accumulated_free_reward,
         sum(pay_reward_exc_cards) over (partition by  BQDate, BatchID, EventName order by MissionPriority) as accumulated_pay_reward,
         sum(free_reward_exc_cards + pay_reward_exc_cards) over (partition by BQDate, BatchID, EventName order by MissionPriority) as accumulated_total_reward
    from (
      select *,
      dense_rank() over(partition by EventName order by BatchIDTs desc) as recent_rank, -- 處理同樣EventName (上錯後覆蓋，取新的)
      from mission_info
    )
    where recent_rank = 1
   -- order by MissionBookMark, MissionPriority  
  )
)


select *, 
       ifnull(threshold_bet - lag(threshold_bet) over (partition by MissionBookMark order by MissionPriority), threshold_bet)  as pursue_bet,
       LPAD(FORMAT("%'d", CAST(threshold_bet AS INT64)), 20, ' ') AS threshold_bet_formatted
from deduplicated_eventname 
order by MissionBookMark, MissionPriority
```

## [BattlePass] 目標二為矩陣
**描述：** 將MissionFeature BPCategory紀錄的資訊 unnest開來，不能JOIN會爆炸

```sql
declare startdate date default '2026-03-01';
declare enddate date default current_date('UTC+8');

with missiondim as (   
  SELECT 
    DISTINCT
      -- MissionBookMark level
      MissionBookMark,
      ActivityType,
      MissionFeatureCHT as purpose,
      GameCategory AS target_metric,
      BatchID,
      BatchIDTs,

      -- EventName level
      EventName,
      REGEXP_REPLACE(EventName, r'_[0-9]{8}_', '_') AS EventName_unit, -- 比MissionBookMark小但比EventName大，將同一MissionBookMark的系列鎖任務拆出來
      BattlePassBuyNumber,
      split(EventName, '_')[offset(4)] as open_vip
  FROM `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
  WHERE BQDate BETWEEN startdate AND enddate 
    AND CountryOperation = 'for' 
    AND Country = 'CN'
    AND ActivityType != 'GU'
    AND MissionBookMark not like '奇喵派對內%'
)

, deduplicated_missiondim as (
  
  select 
    distinct 
      -- MissionBookMark level
      MissionBookMark,
      ActivityType, 
      purpose,
      target_metric,

      -- EventName level
      EventName,
      EventName_unit,
      BattlePassBuyNumber,
      open_vip
  from (
    select *, row_number() over(partition by EventName order by BatchIDTs desc) as recent_rank
    from missiondim
  )
  where recent_rank = 1
)

, user_tag as (
  select 
      extract(month from BQDate) as month,
      UserID,
      NewUserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate between date_trunc(startdate, month) and date_trunc(enddate, month)
      AND Country = 'CN'
)

,  engaged_dau as (
  select distinct mr.BQDate, ut.NewUserTag, mr.EventName,  mr.UserID as engaged_user_id-- count(distinct mr.UserID) as engaged_dau
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog` mr
  inner join user_tag ut
    on extract(month from mr.BQDate) = ut.month and mr.UserID = ut.UserID
  where BQDate between startdate and enddate
    AND Country = 'CN'
  -- group by mr.BQDate, ut.NewUserTag, mr.EventName

), daily_revenue as (
  select 
      distinct
         BQDate, 
         ut.NewUserTag, 
         bpb.UserID as bought_user_id,
         substr(BattlePassID, 4) as EventName,
         BuyNumber as sales 
        --  count(distinct bpb.UserID) as payuser_counts,
        --  sum(BuyNumber) as total_sales
  from `rd7-data-big-query.bklog.BattlePassBuyLog` bpb
  inner join user_tag ut
    on extract(month from bpb.BQDate) = ut.month and bpb.UserID = ut.UserID
  where BQDate between startdate and enddate
    AND Country = 'CN'
  -- group by 1, 2, 3
)


, a  as (
  select ed.*, dr.NewUserTag, dr.bought_user_id, dr.sales, dm.* except (EventName)
  from engaged_dau ed
  full outer join daily_revenue dr
    on ed.BQDate = dr.BQDate and ed.EventName = dr.EventName and ed.engaged_user_id = dr.bought_user_id
  left join deduplicated_missiondim dm
    on ed.EventName = dm.EventName
)

select BQDate, count(distinct MissionBookMark) as mission_counts, count(distinct engaged_user_id) as engaged_dau,
count(distinct bought_user_id) as payuser_counts, sum(sales) as total_sales
from a
group by BQDate
order by BQDate desc

-- select ed.*, 
--        ifnull(dr.payuser_counts, 0) as payuser_counts, 
--        ifnull(dr.total_sales, 0) as total_sales,
--        dm.* except(EventName)
-- from engaged_dau ed
-- left join daily_revenue dr
--   on ed.BQDate = dr.BQDate and ed.NewUserTag = dr.NewUserTag and ed.EventName = dr.EventName
-- inner join deduplicated_missiondim dm -- 排除 奇喵派對內 以及 公會任務
--   on ed.EventName = dm.EventName
-- order by NewUserTag, BQDate
-- ;
```

## [BattlePass] Tableau BP時序分析
**描述：** BP 分析，除了BP指標外還包含了總指標，因為每個BP都是為了要提升總指標用的，故觀察總指標的反應來判斷如何調整BP

```sql
declare startdate date default '2026-01-01';
declare slot_active_threshold int64 default 200;
declare fish_active_threshold int64 default 1000;

with user_tag as (
  select 
      extract(month from BQDate) as month,
      UserID,
      NewUserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate between date_trunc(startdate, month) and date_trunc(current_date('UTC+8') - interval 1 day, month)
)

,  bp_engaged_dau as (
  select mr.BQDate, ut.NewUserTag, count(distinct mr.UserID) as bp_engaged_usercounts
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog` mr
  inner join user_tag ut
    on extract(month from mr.BQDate) = ut.month and mr.UserID = ut.UserID
  where BQDate between startdate and current_date('UTC+8')- interval 1 day
  
  group by mr.BQDate, ut.NewUserTag

), bp_revenue as (
  select BQDate, ut.NewUserTag,
         count(distinct bpb.UserID) as bp_pay_usercounts,
         sum(BuyNumber) as bp_sales
  from `rd7-data-big-query.bklog.BattlePassBuyLog` bpb
  inner join user_tag ut
    on extract(month from bpb.BQDate) = ut.month and bpb.UserID = ut.UserID
  where BQDate between startdate  and current_date('UTC+8') - interval 1 day
  group by 1, 2

), bp_missioncounts as (
  select distinct BQDate, MissionBookMark
  from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
  where BQDate between startdate and current_date('UTC+8') - interval 1 day
    AND CountryOperation = 'for'
    AND Country = 'CN'
    AND ActivityType != 'GU'
    AND MissionBookMark not like '奇喵派對內'



), overall as (
  select dif.BQDate, 
         ut.NewUserTag, 
         count(distinct dif.UserID) as DAU,
         sum (
            case when SlotCoinBetTimes >= slot_active_threshold then 1
            else 0
            end
            ) as slot_active_usercounts,
         sum (
            case when FishCoinBetTimes >= fish_active_threshold then 1
            else 0
            end
            ) as fish_active_usercounts,
          sum(SlotCoinBet) as total_slot_bet,
          sum(FishCoinBet) as total_fish_bet,
          sum(BuyNumber) as total_sales,
          sum(case when BuyNumber > 0 then 1 else 0 end) as total_pay_usercounts
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot` dif
  inner join user_tag ut
    on extract(month from dif.BQDate) = ut.month and dif.UserID = ut.UserID
  where BQDate between '2026-01-01' and current_date('UTC+8')- interval 1 day
    AND Country = 'CN'
  group by 1, 2
) 



select
  o.BQDate,
  o.NewUserTag,
  o.DAU,
  o.slot_active_usercounts,
  o.fish_active_usercounts,
  o.total_slot_bet,
  o.total_fish_bet,
  o.total_sales,
  o.total_pay_usercounts,
  ifnull(bed.bp_engaged_usercounts, 0) as bp_engaged_usercounts,
  ifnull(br.bp_pay_usercounts, 0) as bp_pay_usercounts,
  ifnull(br.bp_sales, 0) as bp_sales,
  count(distinct MissionBookMark) as mission_counts
from overall o
left join bp_engaged_dau bed
  on o.BQDate = bed.BQDate and o.NewUserTag = bed.NewUserTag
left join bp_revenue br
  on o.BQDate = br.BQDate and o.NewUserTag = br.NewUserTag
left join bp_missioncounts bm
  on o.BQDate = bm.BQDate 
group by 1,2,3,4,5,6,7,8,9,10,11,12
order by BQDate desc
;
```

## [BattlePass] Tableau BP 參與狀況分析
**描述：** 顆粒度跟ＭissionCompleteLog相同

```sql
從2026年一月開始，加入EventName_startdate跟enddate，在Tableau就用這兩個篩選，就能夠改用擷取了 

with deduplicated_missiondim as (
  from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` a
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
      and CountryOperation = 'for' 
      and Country = 'CN'
      and ActivityType != 'GU'
      and MissionBookMark not like '奇喵派對內%'
  |> left join (
        select BatchIDTs, EventName, Max(MissionPriority) as max_level
        from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        where BQDate between '2026-01-01' and current_date('UTC+8')
        group by BatchIDTs, EventName
      ) b
        on a.BatchIDTs = b.BatchIDTs and a.EventName = b.EventName
  |> extend 
      REGEXP_REPLACE(a.EventName, r'_[0-9]{8}_', '_') AS EventName_unit,
      split(a.EventName, '_')[offset(4)] as open_vip,
      REGEXP_EXTRACT(a.EventName, r'_(\d{8})_') as which_round,
      parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')) as EventName_startdate,
      date_add(parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')), interval (RunDay - 1) day) as EventName_enddate, 

      case 
        when Rule = 'fish_shot' or Rule like '%bet_times' then TargetTimes * if(JSON_VALUE(AppendRule, '$.fish_room') = 'vip' OR lower(split(MissionBookMark, '_')[3]) like 'vip', 5000, 2000)  
        when Rule = 'slot_spin' then TargetTimes * coalesce(cast(JSON_VALUE(AppendRule, '$.bet') as int64), 500) 
        when Rule like '%bet' or Rule like '%win' then TargetTimes 
        else -1 
      end as threshold_bet,
      MissionPriority / b.max_level as completion_ratio
  |> select
      distinct 
        MissionBookMark, ActivityType, MissionFeatureCHT as purpose, GameCategory AS target_metric, BatchID, a.BatchIDTs, 
        a.EventName, EventName_unit, BattlePassBuyNumber, open_vip, which_round, EventName_startdate, EventName_enddate,b.max_level,
        MissionID, MissionPriority, MissionName, Rule, TargetTimes, threshold_bet, completion_ratio
  |> extend dense_rank() over(partition by EventName order by BatchIDTs desc) as recent_rank
  |> where recent_rank = 1
  |> select 
      distinct
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, BattlePassBuyNumber, open_vip, which_round, EventName_startdate, EventName_enddate, max_level,
        MissionID, MissionPriority, MissionName, TargetTimes, Rule, threshold_bet,
        round(completion_ratio, 2) as completion_ratio
)

-- 1. 構造 MissionPriority = 0 的任務曝光維度資料
, missiondim_0 as (
  from deduplicated_missiondim dm
  |> select
      distinct
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, BattlePassBuyNumber, open_vip, which_round, EventName_startdate, EventName_enddate, max_level
  |> extend 
      CONCAT(EventName, '_0') as MissionID,
      0 as MissionPriority,
      '任務曝光' as MissionName,
      0 as TargetTimes,
      'Impression' as Rule,
      0 as threshold_bet,
      0.0 as completion_ratio
  |> select 
      distinct 
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, BattlePassBuyNumber, open_vip, which_round, EventName_startdate, EventName_enddate, max_level,
        MissionID, MissionPriority, MissionName, TargetTimes, Rule, threshold_bet, completion_ratio
)

-- 2. 將原維度表與第 0 階維度表聯集
, final_missiondim as (
  select * from deduplicated_missiondim
  UNION ALL
  select * from missiondim_0
)

, user_tag as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate between date_trunc('2026-01-01', month) and date_trunc(current_date('UTC+8'), month)
  |> extend extract(month from BQDate) as month
  |> select month, UserID, NewUserTag
)

-- 3. 原本的過關紀錄
, mission_complete as (
  from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
  |> extend extract(month from BQDate) as month
  |> left join user_tag ut 
        using(month, UserID)
  |> select 
      distinct
        BQDate as finished_date, 
        ut.NewUserTag,
        UserID as finished_user_id,
        MissionID
)

-- 4. 曝光紀錄
, mission_impression as (
  from `rd7-data-big-query.bklog.ActivityMissionPopUpStateLog`
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
  |> extend 
      extract(month from BQDate) as month,
      CONCAT(EventName, '_0') as MissionID   -- 提前組合出 _0 的 MissionID
  |> left join user_tag ut 
        using(month, UserID)
  |> select 
      distinct
        BQDate as finished_date, 
        ut.NewUserTag,
        UserID as finished_user_id,
        MissionID
)

-- 5. 將「曝光紀錄」與「過關紀錄」聯集
, all_user_mission_events as (
  select * from mission_complete
  UNION ALL
  select * from mission_impression
)

-- 6. 最終的 JOIN (以補齊了0階的 final_missiondim 作為主表)
from final_missiondim dm
|> left join all_user_mission_events mc 
      using(MissionID)
|> select 
      dm.*, 
      mc.finished_date, 
      mc.NewUserTag, 
      mc.finished_user_id
```

## [BattlePass] Tableau BP 領獎狀況
**描述：** 顆粒度跟MissionRewardLog相同，用這個來算每個任務累積的押量

```sql
可擷取
with mission_info as (
  from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` a
  |>where BQDate between '2026-01-01' and current_date('UTC+8')
      AND CountryOperation = 'for'
      AND Country = 'CN'
      AND ActivityType != 'GU'
      AND MissionBookMark not like '奇喵派對內%'
  |>left join (
        select BatchIDTs, EventName, Max(MissionPriority) as max_level
        from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        where BQDate between '2026-01-01' and current_date('UTC+8')
        group by BatchIDTs, EventName
      ) b
        on  a.BatchIDTs = b.BatchIDTs and a.EventName = b.EventName
  |>extend 
      REGEXP_REPLACE(a.EventName, r'_[0-9]{8}_', '_') AS EventName_unit,
      split(a.EventName, '_')[offset(4)] as open_vip,
      REGEXP_EXTRACT(a.EventName, r'_(\d{8})_') as which_round,
      parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')) as EventName_startdate,
      date_add(parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')), interval (RunDay - 1) day) as EventName_enddate, 
      case 
        when Rule = 'fish_shot' or Rule like '%bet_times' then  TargetTimes * if(JSON_VALUE(AppendRule, '$.fish_room') = 'vip' OR lower(split(MissionBookMark, '_')[3]) like  'vip',5000,2000)  
        when Rule = 'slot_spin' then TargetTimes * coalesce(cast(JSON_VALUE(AppendRule, '$.bet') as int64), 500) 
        when Rule like '%bet' or Rule like '%win' then TargetTimes 
        else -1 
      end as threshold_bet,
      MissionPriority / b.max_level as completion_ratio
  |>select
      distinct 
        -- MissionBookMark level
        MissionBookMark,
        ActivityType,
        MissionFeatureCHT as purpose,
        GameCategory AS target_metric,
        BatchID,
        a.BatchIDTs,

        -- EventName level
        a.EventName,
        EventName_unit,
        BattlePassBuyNumber,
        open_vip, 
        which_round,
        EventName_startdate,
        EventName_enddate,
        b.max_level,
        runday,

        -- MissionPriority level
        MissionID,
        MissionPriority,
        MissionName,
        Rule,
        TargetTimes,
        threshold_bet,
        completion_ratio
  |> extend dense_rank() over(partition by EventName order by BatchIDTs desc) as recent_rank
  |> where recent_rank = 1
  |>select 
      distinct
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, BattlePassBuyNumber, open_vip, which_round, EventName_startdate, EventName_enddate, max_level, runday,
        MissionID, MissionPriority, MissionName, TargetTimes, Rule, threshold_bet,
        round(completion_ratio,2) as completion_ratio
)

, user_tag as (
  select 
      extract(month from BQDate) as month,
      UserID,
      NewUserTag
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    where BQDate between date_trunc('2026-01-01', month) and date_trunc(current_date('UTC+8'), month)
)

, reward_log as (
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog` 
  |> where BQDate >= '2026-01-01'
  |> extend 
      extract(month from BQDate) as month
  |> extend   
      row_number() over(partition by UserID, EventName order by MissionPriority desc) as rewarded_level_rank 
  |> where rewarded_level_rank = 1 # 計算押量型任務的累積押量時，需要每個玩家追到的最高門檻加總
  |> select BQDate, month, UserID, MissionID 
)


from mission_info mi
|> left join reward_log rl
      using(MissionID)
|> left join user_tag ut
      using(month, UserID)
|> select mi.*, rl.BQDate, rl.UserID, ut.NewUserTag
```

## [BattlePass] Tableau BP 營收狀況(BP角度)
**描述：** 顆粒度到EventName + UserID(主表為MissionDim)

```sql
整合了訂單角度所需資料，並且包含沒被購買的任務
with dim_usertags as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`  # 抓到前一天的資料，當天的新登入用戶不會有資料
  |> where BQDate >= '2026-01-01'
  |> extend extract(month from BQDate) as month
  |> select month, UserID, NewUserTag, UserTag
)

, dim_mission as (
  from `rd7-data-big-query.preprocessed_bklog.MissionList`
  |> where MissionStartDate >= '2025-11-01' # MissionStartDate 為 partition 依據，節省流量用
      and MissionStartDate <= date_sub(current_date('Asia/Taipei'), interval 1 day) 
      and MissionEndDate >= '2026-01-01' # 抓2026有上線的任務
  |> extend
      split(EventName, '_')[safe_offset(0)] as ActivityType,
      split(EventName, '_')[safe_offset(4)] as open_vip,
      split(EventName, '_')[safe_offset(5)] as CountryOperation,
      split(EventName, '_')[safe_offset(6)] as Country,
      REGEXP_REPLACE(EventName, r'_[0-9]{8}_', '_') AS EventName_unit,
      concat(cast(MissionStartDate as string), ' to ', cast(MissionEndDate as string)) as which_round,
      array_length(json_query_array(MissionLevelInfo, '$')) as max_level 
)


, fact_buylog as (
  from `rd7-data-big-query.bklog.BattlePassBuyLog` # order-level
  |> where BQDate between '2026-01-01' and date_sub(current_date('Asia/Taipei'), interval 1 day)
        and BuyResult = 1
  |> set EventTime = datetime(timestamp_seconds(EventTime), 'Asia/Taipei')
  |> rename
      BQDate as order_date,
      UserID as buyer_UserID,
      VipLV as buyer_VipLV,
      Country as buyer_Country
  |> extend 
        substr(BattlePassID, 4) as EventName,
        extract( month from order_date) as order_month
  |> select order_month, order_date, EventTime, buyer_UserID, buyer_VipLV, buyer_Country, BuyNumber, VIPPointAwarded, BattlePassID, EventName, OrderID
)

from dim_mission dm
|> left join fact_buylog fb
    using(EventName)
|> left join dim_usertags du
    on fb.order_month = du.month and fb.buyer_UserID = du.UserID
|> select * except(month, UserID)
;
```

## [BattlePass] Tableau BP 營收(訂單角度)
**描述：** 主表為BattlePassBuyLog，計算的是每日的營收(會包含非起始日開的任務，而是以前開但持續至今的)

```sql
with user_tags as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`  # 抓到前一天的資料，當天的新登入用戶不會有資料
  |> where BQDate >= '2026-01-01'
  |> extend extract(month from BQDate) as month
  |> select month, UserID, NewUserTag, UserTag
)

, dim_mission as (
  from `rd7-data-big-query.preprocessed_bklog.MissionList`
  |> where MissionStartDate >= '2025-12-01' and MissionStartDate <= current_date('Asia/Taipei') # MissionStartDate 為 partition 依據，節省流量用
      and MissionEndDate >= '2026-01-01' # 抓2026有上線的任務
  |> extend
      split(EventName, '_')[safe_offset(0)] as ActivityType,
      split(EventName, '_')[safe_offset(4)] as open_vip,
      split(EventName, '_')[safe_offset(5)] as CountryOperation,
      split(EventName, '_')[safe_offset(6)] as Country,
      REGEXP_REPLACE(EventName, r'_[0-9]{8}_', '_') AS EventName_unit,
      concat(cast(MissionStartDate as string), ' to ', cast(MissionEndDate as string)) as which_round,
      array_length(json_query_array(MissionLevelInfo, '$')) as max_level 
)

from `rd7-data-big-query.bklog.BattlePassBuyLog`
|> where BQDate between '2026-01-01' and date_sub(current_date('Asia/Taipei'), interval 1 day)
      and BuyResult = 1
|> set EventTime = datetime(timestamp_seconds(EventTime), 'Asia/Taipei')
|> rename
    BQDate as order_date,
    UserID as buyer_UserID,
    VipLV as buyer_VipLV,
    Country as buyer_Country
|> extend 
      substr(BattlePassID, 4) as EventName,
      extract( month from order_date) as order_month
|> select order_month, order_date, EventTime, buyer_UserID, buyer_VipLV, buyer_Country, BuyNumber, VIPPointAwarded, BattlePassID, EventName, OrderID
|> as bpb
|> inner join user_tags ut
        on bpb.order_month = ut.month and bpb.buyer_UserID = ut.UserID
|> select * except(month, UserID)
|> as fact
|> left join dim_mission dm
    using(EventName)
|> select order_month, order_date, EventTime, OrderID, buyer_UserID, buyer_VipLV, buyer_Country, NewUserTag, UserTag, EventName, BuyNumber, VIPPointAwarded, BattlePassID, MissionUUID, MissionLevelInfo, GameCategory, MissionFeature, MissionFeatureCHT, GameType, ActivityGameID, GameID, MissionBookMark, MissionStartDate, MissionEndDate, ActivityStartTime, ActivityEndTime, BatchID, RunDay, BreakDay, ActivityTYpe, open_vip, CountryOperation, Country, EventName_unit, which_round, max_level
|> order by EventTime desc
```

## [Analysis] 為何2月虎機遊玩人數以及活動參與人數大掉
**描述：** 虎機遊玩人數大部分掉在馬雅(沒開奇喵沒得洗帳號，故新手訓練的遊玩人數大掉); 活動參與人數大部分掉在奇喵派對內跟節慶活動活躍

```sql
with 

# 所有玩家在當月的標籤(未排除國家)
usertags as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate >= '2026-01-01'
  |> extend extract(month from BQDate) as tag_month
  |> select tag_month, UserID, NewUserTag
  |> distinct
)

, mission_info as (
  from `rd7-data-big-query.preprocessed_bklog.MissionListDetail`
  |> where MissionEndDate >= '2026-01-01'
        and MissionStartDate <= current_date('UTC+8')
  |> select EventName
)

from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
|> where BQDate >= '2026-01-01'
      and Country = 'CN'
|> extend extract(month from BQDate) as reward_month
|> as amd
|> left join usertags ut
    on amd.reward_month = ut.tag_month and amd.UserID = ut.UserID
|> left join mission_info mi
    on amd.MissionID = mi.MissionID
# 確認哪個任務的無客、迷你客參與人數大掉，結論-奇喵派對內
|> where NewUserTag in ('無客', '迷你客')
|> aggregate count(distinct amd.UserID) as engaged_dau
    group by reward_month, MissionBookMark
|> order by reward_month, engaged_dau desc

# 確認掉的人數來自於無客、迷你客
|> aggregate count(distinct amd.UserID) as oneday_usercounts
    group by reward_month, BQDate, ut.NewUserTag
|> aggregate avg(oneday_usercounts) as daily_avg_usercounts
    group by reward_month, NewUserTag
|> order by NewUserTag, reward_month
|> pivot(
      max(daily_avg_usercounts)
      for reward_month in (1, 2, 3)
      )
|> extend 
    (_2 - _1)/ _1 as _1_2_growth_rate,
    (_3 - _2)/ _2 as _2_3_growth_rate
```

## [Analysis] 2月BP付費人數掉的原因
**描述：** # 確認整月的distinct 付費人數是否掉
from `rd7-data-big-query.bklog.BattlePassBuyLog`
|> where BQDate between '2026-01-01' and '2026-02-28'
    and Country = 'CN'
|> extend extract(month from BQDate) as buy_month
|> aggregate count(distinct UserID)
    group by buy_month
;

# 一月有消費二月沒消費的玩家，在一月都在買啥
from `rd7-data-big-query.bklog.BattlePassBuyLog`
|> where BQDate between '2026-01-01' and '2026-01-31'
    and Country = 'CN'
    and UserID not in (
        from `rd7-data-big-query.bklog.BattlePassBuyLog`
        |> where BQDate between '2026-02-01' and '2026-02-28'
            and Country = 'CN'
        |> select distinct UserID)
    and UserID in (
        from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
        |> where BQDate between '2026-02-01' and '2026-02-28'
            and Country = 'CN'
        |> select distinct UserID
    )
|> extend substring(BattlePassID, 4) as EventName
|> left join 
        (
        from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        |> where BQDate between '2026-01-01' and '2026-01-31'
                and CountryOperation = 'for'
                and Country = 'CN'
        |> select distinct EventName, MissionBookMark
        )
    using(EventName)
|> aggregate count(*) as ordercounts
    group by MissionBookMark
|> order by ordercounts desc
;

# 一月有消費二月沒消費的玩家，但還是有玩的玩家人數(530位是一月有消費二月無消費的人，其中340位是二月仍然有在玩的)
with jan_bp_buyers as (
  from `rd7-data-big-query.bklog.BattlePassBuyLog`
  |> where BQDate between '2026-01-01' and '2026-01-31'
     and Country = 'CN'
  |> select distinct UserID
)

, feb_bp_buyers as (
  from `rd7-data-big-query.bklog.BattlePassBuyLog`
  |> where BQDate between '2026-02-01' and '2026-02-28'
     and Country = 'CN'
  |> select distinct UserID
)

, feb_active_users as (
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  |> where BQDate between '2026-02-01' and '2026-02-28'
     and Country = 'CN'
  |> select distinct UserID
)

from jan_bp_buyers a
|> left join feb_bp_buyers b using(UserID)
|> where b.UserID is null
|> inner join feb_active_users c using(UserID) 
|> select a.UserID

```sql
# 確認整月的distinct 付費人數是否掉
from `rd7-data-big-query.bklog.BattlePassBuyLog`
|> where BQDate between '2026-01-01' and '2026-02-28'
    and Country = 'CN'
|> extend extract(month from BQDate) as buy_month
|> aggregate count(distinct UserID)
    group by buy_month
;

# 一月有消費二月沒消費的玩家，在一月都在買啥
from `rd7-data-big-query.bklog.BattlePassBuyLog`
|> where BQDate between '2026-01-01' and '2026-01-31'
    and Country = 'CN'
    and UserID not in (
        from `rd7-data-big-query.bklog.BattlePassBuyLog`
        |> where BQDate between '2026-02-01' and '2026-02-28'
            and Country = 'CN'
        |> select distinct UserID)
    and UserID in (
        from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
        |> where BQDate between '2026-02-01' and '2026-02-28'
            and Country = 'CN'
        |> select distinct UserID
    )
|> extend substring(BattlePassID, 4) as EventName
|> left join 
        (
        from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        |> where BQDate between '2026-01-01' and '2026-01-31'
                and CountryOperation = 'for'
                and Country = 'CN'
        |> select distinct EventName, MissionBookMark
        )
    using(EventName)
|> aggregate count(*) as ordercounts
    group by MissionBookMark
|> order by ordercounts desc
;

# 一月有消費二月沒消費的玩家，但還是有玩的玩家人數(530位是一月有消費二月無消費的人，其中340位是二月仍然有在玩的)
with jan_bp_buyers as (
  from `rd7-data-big-query.bklog.BattlePassBuyLog`
  |> where BQDate between '2026-01-01' and '2026-01-31'
     and Country = 'CN'
  |> select distinct UserID
)

, feb_bp_buyers as (
  from `rd7-data-big-query.bklog.BattlePassBuyLog`
  |> where BQDate between '2026-02-01' and '2026-02-28'
     and Country = 'CN'
  |> select distinct UserID
)

, feb_active_users as (
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  |> where BQDate between '2026-02-01' and '2026-02-28'
     and Country = 'CN'
  |> select distinct UserID
)

from jan_bp_buyers a
|> left join feb_bp_buyers b using(UserID)
|> where b.UserID is null
|> inner join feb_active_users c using(UserID) 
|> select a.UserID
```

## [Analysis] 1、2月BP 參與率
**描述：** 分析二月切受眾重新抓門檻後是否有提升參與度

```sql
create temp table final_data as 

with deduplicated_missiondim as (
  from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` a
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
      and CountryOperation = 'for' 
      and Country = 'CN'
      and ActivityType != 'GU'
      and MissionBookMark not like '奇喵派對內%'
  |> left join (
        select BatchIDTs, EventName, Max(MissionPriority) as max_level
        from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        where BQDate between '2026-01-01' and current_date('UTC+8')
        group by BatchIDTs, EventName
      ) b
        on a.BatchIDTs = b.BatchIDTs and a.EventName = b.EventName
  |> extend 
      REGEXP_REPLACE(a.EventName, r'_[0-9]{8}_', '_') AS EventName_unit,
      parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')) as EventName_startdate,
      date_add(parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')), interval (RunDay - 1) day) as EventName_enddate, 

      MissionPriority / b.max_level as completion_ratio
  |> select
      distinct 
        MissionBookMark, ActivityType, MissionFeatureCHT as purpose, GameCategory AS target_metric, BatchID, a.BatchIDTs, 
        a.EventName, EventName_unit, EventName_startdate, EventName_enddate,b.max_level,
        MissionID, MissionPriority, MissionName, completion_ratio
  |> extend dense_rank() over(partition by EventName order by BatchIDTs desc) as recent_rank
  |> where recent_rank = 1
  |> select 
      distinct
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, EventName_startdate, EventName_enddate, max_level,
        MissionID, MissionPriority, MissionName, round(completion_ratio, 2) as completion_ratio
  |> where EventName_startdate >= '2026-01-01'
)

-- 1. 構造 MissionPriority = 0 的任務曝光維度資料
, missiondim_0 as (
  from deduplicated_missiondim dm
  |> select
      distinct
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, EventName_startdate, EventName_enddate, max_level
  |> extend 
      CONCAT(EventName, '_0') as MissionID,
      0 as MissionPriority,
      '任務曝光' as MissionName,
      0.0 as completion_ratio
  |> select 
      distinct 
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit,EventName_startdate, EventName_enddate, max_level,
        MissionID, MissionPriority, MissionName, completion_ratio
)

-- 2. 將原維度表與第 0 階維度表聯集
, final_missiondim as (
  select * from deduplicated_missiondim
  UNION ALL
  select * from missiondim_0
)

-- 玩家當月標籤:未排國家
, user_tag as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate between date_trunc('2026-01-01', month) and date_trunc(current_date('UTC+8'), month)
      and UserID not in (select distinct UserID from `rd7-data-big-query.App_Dragon.GameAccount`)
  |> extend extract(month from BQDate) as month
  |> select month, UserID, NewUserTag
)

-- 3. 原本的過關紀錄: 未排國家，主表MissionDim已篩國家
, mission_complete as (
  from `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
  |> extend extract(month from BQDate) as month
  |> inner join user_tag ut 
        using(month, UserID)
  |> select 
      distinct
        -- BQDate as finished_date, 
        ut.NewUserTag,
        UserID as finished_user_id,
        MissionID
)

-- 4. 曝光紀錄
, mission_impression as (
  from `rd7-data-big-query.bklog.ActivityMissionPopUpStateLog`
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
  |> extend 
      extract(month from BQDate) as month,
      CONCAT(EventName, '_0') as MissionID   -- 提前組合出 _0 的 MissionID
  |> inner join user_tag ut 
        using(month, UserID)
  |> select 
      distinct
        -- BQDate as finished_date, 
        ut.NewUserTag,
        UserID as finished_user_id,
        MissionID
)

-- 5. 將「曝光紀錄」與「過關紀錄」聯集
, all_user_mission_events as (
  select * from mission_complete
  UNION ALL
  select * from mission_impression
)

-- 6. 最終的 JOIN (已補齊了0階的 final_missiondim 作為主表)
, final_data as (
  from final_missiondim dm
  |> left join all_user_mission_events mc 
        using(MissionID)
  |> select 
        dm.*, 
        -- mc.finished_date, 
        mc.NewUserTag, 
        mc.finished_user_id
)
select *
from final_data
;

# 看各月份整體的參與率
from final_data
|> extend
    extract(month from EventName_Startdate) as mission_month
|> aggregate  
      count(distinct case when MissionPriority = 0 then finished_user_id end) as impressed_usercounts,
      count(distinct case when MissionPriority != 0 then finished_user_id end) as engaged_usercounts
    group by mission_month, MissionBookMark, EventName_unit, EventName
|> aggregate
      safe_divide(sum(engaged_usercounts), sum(impressed_usercounts)) as engagement_rate
    group by mission_month, MissionBookMark, EventName_unit
|> set engagement_rate = if( engagement_rate >= 1, 1, engagement_rate)  
|> aggregate avg(engagement_rate)
    group by mission_month
|> order by mission_month
;
# 看各月份整體的參與率: 排除「福利型」任務
from final_data
|> where MissionBookMark not like '%福利%'
|> extend
    extract(month from EventName_Startdate) as mission_month
|> aggregate  
      count(distinct case when MissionPriority = 0 then finished_user_id end) as impressed_usercounts,
      count(distinct case when MissionPriority != 0 then finished_user_id end) as engaged_usercounts
    group by mission_month, MissionBookMark, EventName_unit, EventName
|> aggregate
      safe_divide(sum(engaged_usercounts), sum(impressed_usercounts)) as engagement_rate
    group by mission_month, MissionBookMark, EventName_unit
|> set engagement_rate = if( engagement_rate >= 1, 1, engagement_rate)  
|> aggregate avg(engagement_rate)
    group by mission_month
|> order by mission_month
;

# 看各月份的平均完成門檻: 有完成的人最高完成幾成取平均
from final_data
|> where MissionPriority != 0
|> extend
    rank() over(partition by EventName, finished_user_id order by MissionPriority desc) as level_rank,
    extract(month from EventName_Startdate) as mission_month
|> where level_rank = 1
|> aggregate avg(completion_ratio) as avg_completion_ratio
    group by mission_month, MissionBookMark, EventName_unit
|> aggregate avg(avg_completion_ratio)
    group by mission_month
;
# 看各月份的平均完成門檻: 排除「福利型」任務
from final_data
|> where MissionPriority != 0
    and MissionBookMark not like '%福利%'
|> extend
    rank() over(partition by EventName, finished_user_id order by MissionPriority desc) as level_rank,
    extract(month from EventName_Startdate) as mission_month
|> where level_rank = 1
|> aggregate avg(completion_ratio) as avg_completion_ratio
    group by mission_month, MissionBookMark, EventName_unit
|> aggregate avg(avg_completion_ratio)
    group by mission_month
;
```

## [Analysis] 1、2月針對指定大客和超大客開連續登入活動
**描述：** 登入活動是否有效提升玩家在平台上待的天數，且該玩家的日均營收貢獻是否大於登入活動留住的天數(是否划算)

```sql
留存

with deduplicated_missiondim as (
  from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog` a
  |> where BQDate between '2026-01-01' and current_date('UTC+8')
      and CountryOperation = 'for' 
      and Country = 'CN'
      and ActivityType != 'GU'
      and MissionBookMark not like '奇喵派對內%'
  |> left join (
        select BatchIDTs, EventName, Max(MissionPriority) as max_level
        from `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
        where BQDate between '2026-01-01' and current_date('UTC+8')
        group by BatchIDTs, EventName
      ) b
        on a.BatchIDTs = b.BatchIDTs and a.EventName = b.EventName
  |> extend 
      REGEXP_REPLACE(a.EventName, r'_[0-9]{8}_', '_') AS EventName_unit,
      parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')) as EventName_startdate,
      date_add(parse_date('%Y%m%d', REGEXP_EXTRACT(a.EventName, r'_(\d{8})_')), interval (RunDay - 1) day) as EventName_enddate, 

      MissionPriority / b.max_level as completion_ratio
  |> select
      distinct 
        MissionBookMark, ActivityType, MissionFeatureCHT as purpose, GameCategory AS target_metric, BatchID, a.BatchIDTs, 
        a.EventName, EventName_unit, EventName_startdate, EventName_enddate,b.max_level, RunDay,
        MissionID, MissionPriority, MissionName, completion_ratio
  |> extend dense_rank() over(partition by EventName order by BatchIDTs desc) as recent_rank
  |> where recent_rank = 1
  |> select 
      distinct
        MissionBookMark, ActivityType, purpose, target_metric,
        EventName, EventName_unit, EventName_startdate, EventName_enddate, max_level, RunDay,
        MissionID, MissionPriority, MissionName, round(completion_ratio, 2) as completion_ratio
  |> where EventName_startdate >= '2026-01-01'
  # 登入活躍任務
      and MissionBookMark like '%登入%'
      and cast(split(EventName_unit, '_')[offset(2)] as int64) != 2 -- 排除上錯的登入活動
      and EventName != 'SP_LV1_20260114_3_v123456_for_cn_G'  -- 排除社交條件任務
  |> select distinct MissionBookMark, EventName_unit, EventName, EventName_startdate, EventName_enddate, RunDay
  |> extend 
       DATE_SUB(EventName_startdate, INTERVAL RunDay DAY) as pre_event_startdate,
       DATE_SUB(EventName_startdate, INTERVAL 1 DAY) as pre_event_enddate
  |> select distinct 
       MissionBookMark, EventName_unit, EventName, 
       EventName_startdate, EventName_enddate, 
       pre_event_startdate, pre_event_enddate, RunDay
)

-- 1. 抓出玩家在該活動的「首次領獎日 (Day 0)」
, user_first_claim as (
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
  |> where BQDate >= '2026-01-01'
  |> inner join deduplicated_missiondim dm 
       using(EventName)
  -- 🌟 關鍵：用 MIN(BQDate) 找出首次領獎日，完美解決單次領取多獎項產生多 rows 的問題
  |> aggregate MIN(BQDate) as first_claim_date
     group by dm.EventName_unit, EventName, UserID
)

  -- 2. 串接玩家登入日誌，計算每次登入距離首次領獎日過了幾天
  from user_first_claim fc
  |> left join (
       select distinct UserID, BQDate 
       from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot` 
       where BQDate >= '2026-01-01'
     ) snap
     on fc.UserID = snap.UserID
     -- 只看領獎當天 (Day 0) 以及後續 14 天內的登入紀錄
     and snap.BQDate between fc.first_claim_date and DATE_ADD(fc.first_claim_date, INTERVAL 14 DAY)
  -- 算出現有登入日期與 Day 0 的天數差
  |> extend DATE_DIFF(snap.BQDate, fc.first_claim_date, DAY) as days_since_first_claim
  -- 3. 活動層級聚合：計算 N 日留存人數與留存率
  |> aggregate
      -- Day 0 的登入人數，代表「該活動實際觸發領獎的總人數」（作為留存率分母）
      COUNT(DISTINCT CASE WHEN days_since_first_claim = 0 THEN fc.UserID END) as cohort_users,
      -- 分別計算第 1, 3, 7 天有登入的人數
      COUNT(DISTINCT CASE WHEN days_since_first_claim = 1 THEN fc.UserID END) as d1_retained,
      COUNT(DISTINCT CASE WHEN days_since_first_claim = 3 THEN fc.UserID END) as d3_retained,
      COUNT(DISTINCT CASE WHEN days_since_first_claim = 7 THEN fc.UserID END) as d7_retained
    group by EventName_unit, EventName
  -- 延伸計算成百分比率
  |> extend
      ROUND(SAFE_DIVIDE(d1_retained, cohort_users), 4) as d1_retention_rate,
      ROUND(SAFE_DIVIDE(d3_retained, cohort_users), 4) as d3_retention_rate,
      ROUND(SAFE_DIVIDE(d7_retained, cohort_users), 4) as d7_retention_rate
  |> order by EventName_startdate DESC, EventName
```

## [Analysis] 123月押量是否提升
**描述：** 透過篩出各月份有確實有在玩BP的玩家，並觀察各客群有在玩˙BP的人均押量是否提升

```sql
# 有參與BP的玩家押量是否上升
with user_tag as (

  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate between date_trunc('2026-01-01', month) and date_trunc(current_date('UTC+8'), month)
      and UserID not in (select distinct UserID from `rd7-data-big-query.App_Dragon.GameAccount`)
      and UserID not in (select distinct UserID 
                        from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot` 
                        where BQDate >= '2026-01-01' 
                          and 9035 in unnest(Status))
      and UserID not in (select distinct UserID 
                        from `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog` 
                        where BQDate <= date_sub(current_date('UTC+8'), interval 31 DAY))
      and Country = 'CN'
  |> extend extract(month from BQDate) as tag_month
  |> select tag_month, UserID, NewUserTag)

, bp_engaged_user as (
  
  from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
  |> where BQDate between '2026-01-01' and '2026-01-15'
      or BQDate between '2026-02-01' and '2026-02-15'
      or BQDate between '2026-03-01' and '2026-03-15'
  |> extend extract(month from BQDate) as claim_month
  |> aggregate 
      count(distinct BQDate) as claimed_days, 
      count(distinct MissionID) as claimed_counts
     group by claim_month, UserID
  |> where 
      claimed_counts >= 3
      -- and claimed_days >= 3
  |> select distinct claim_month, UserID
)

, metrics as (

  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  |> where BQDate between '2026-01-01' and '2026-01-15'
      or BQDate between '2026-02-01' and '2026-02-15'
      or BQDate between '2026-03-01' and '2026-03-15'
  |> extend extract(month from BQDate) as month
  |> aggregate 
        sum(FishCoinBet) as fishtotalbet,
        sum(SlotCoinBet) as slottotalbet
      group by month, UserID
)

from user_tag ut
|> inner join bp_engaged_user eu
    on ut.tag_month = eu.claim_month and ut.UserID = eu.UserID
|> left join metrics me
    on ut.tag_month = me.month and ut.UserID = me.UserID
|> where month is not null   
|> aggregate 
    sum(slottotalbet) as slottotalbet,
    count( distinct case when slottotalbet != 0 then me.UserID end) as slot_usercounts,
    sum(fishtotalbet) as fishtotalbet,
    count( distinct case when fishtotalbet != 0 then me.UserID end ) as fish_usercounts,
  group by tag_month, NewUserTag
|> extend 
    slottotalbet / slot_usercounts as slot_ppl_avg_bet,
    fishtotalbet / fish_usercounts as fish_ppl_avg_bet
|> order by NewUserTag, tag_month
```

## [BattlePass] 滿額任務AB Testi 回應率估算

```sql
from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
|> where BQDate between '2026-01-01' and '2026-01-31'
      and Country = 'CN'
      and 9035 not in unnest(Status)
|> aggregate count(distinct UserID) as dau
    group by BQDate
|> as a    
|> left join (
              from `rd7-data-big-query.bklog.ActivityMissionPopUpStateLog`
              |> where BQDate between '2026-01-01' and '2026-01-31'
                  and EventName in 
                            (
                            from `rd7-data-big-query.preprocessed_bklog.MissionList`
                            |> where BatchID = '2026-01-01#a5660'
                            |> select distinct EventName
                            )
              |> aggregate count(distinct UserID) as impressed_usercounts
                  group by BQDate
            ) b
        on a.BQDate = b.BQDate
|> extend 
      impressed_usercounts / dau as impression_conversion
|> select a.*, impressed_usercounts, impression_conversion
|> order by BQDate
|> aggregate avg(impression_conversion)
```

## [Others] 客群轉移矩陣
**描述：** 指定月份的錢一月與當月的客群轉移狀況以及占比

```sql
from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
|> where BQDate = '2026-03-01'
   and Country = 'CN'
-- 1. 把原本的 group by 換成 CUBE，讓系統自動產生各維度的小計與總計
|> aggregate count(distinct UserID) as user_count
   group by CUBE(UserTag, NewUserTag)
-- 2. 將 CUBE 自動產生的 NULL 空白欄位，正式替換成字串 '總計'
|> set 
     UserTag = COALESCE(UserTag, '總計'),
     NewUserTag = COALESCE(NewUserTag, '總計')
-- 3. 進行 PIVOT，記得在清單的最後面補上 '總計' 欄位
|> PIVOT(
     SUM(user_count)
     FOR NewUserTag IN ('無客', '迷你客', '小客', '中客', '大客', '超大客', '負貢獻', '總計')
   )
-- 4. 排序優化：確保「總計」列乖乖排在整張報表的最下方
|> order by
    case 
      when UserTag = '無客' then 0
      when UserTag = '迷你客' then 1
      when UserTag = '小客' then 2
      when UserTag = '中客' then 3
      when UserTag = '大客' then 4
      when UserTag = '超大客' then 5
      when UserTag = '負貢獻' then 6
      when UserTag = '總計' then 7
    end 
;

from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
|> where BQDate = '2026-03-01'
    and Country = 'CN'
    and UserTag = '中客'
|> extend count(distinct UserID) over() as feb_medium_usercounts
|> aggregate count(distinct UserID) as new_counts
    group by NewUserTag, feb_medium_usercounts
|> extend
    new_counts / feb_medium_usercounts as percent
|> order by percent desc
```

## [BattlePass] 老虎機指定機台BP門檻參考
**描述：** 依照各個玩家在其「最喜歡的單一機台」上，連n day的押量分布

```sql
# 要開幾天的活動要手調，因為window function的frame expression不接受變數
declare recent_n_day int64 default 21; # 若recent_n_day取太長會使指定機台的押量被稀釋


# 指定機台任務: 依照玩家最喜歡機台的押量代表該玩家在單一機台的最大潛力
with DailyGameBet as (
    from `rd7-data-big-query.bklog.SessionBetWinLog`
    |> where BQDate between 
                        date_sub(current_date('UTC+8'), interval recent_n_day day)
                        and date_sub(current_date('UTC+8'), interval 1 day)
            and Country = 'CN'
            and TotalBet > 0
    |> aggregate sum(TotalBet) as daily_game_bet
        group by UserID, BQDate, GameID
    |> extend extract(month from BQDate) as bet_month
    |> select UserID, BQDate, bet_month, GameID, daily_game_bet
)

# 最喜愛機台的時間要切細點: 若喜愛機台只維持7天，那average會太小
, UserFavoriteGame as (
    from DailyGameBet
    |> aggregate sum(daily_game_bet) as TotalGameBet
        group by UserID, GameID
    |> extend row_number() over(partition by UserID order by TotalGameBet desc) as rk
    |> where rk = 1
    |> select UserID, GameID
)

, DailyTopGameBet as (
    from DailyGameBet dgb
    |> inner join UserFavoriteGame ufg
        on dgb.UserID = ufg.UserID and dgb.GameID = ufg.GameID
    |> select dgb.UserID, dgb.BQDate, dgb.bet_month, dgb.daily_game_bet as daily_bet 
)

, user_tag as (
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    |> where BQDate >= date_trunc(date_sub(current_date('UTC+8'), interval recent_n_day day), month)
    |> extend extract(month from BQDate) as tag_month
    |> select tag_month, UserID, NewUserTag, UserTag
)

, tagged_DailyTopGameBet as (
    from DailyTopGameBet dtgb
    |> inner join user_tag ut
        on dtgb.UserID = ut.UserID and dtgb.bet_month = ut.tag_month
    |> select dtgb.*, ut.NewUserTag
)

, RollingBet as (
    from tagged_DailyTopGameBet
    |> extend sum(daily_bet) over(
                                    partition by UserID, NewUserTag 
                                    order by unix_date(BQDate)
                                    range between 6 preceding and current row
                                 ) as total_rolling_bet
    |> select UserID, NewUserTag, total_rolling_bet
)

, PlayerRepresentativeBet as (
    from RollingBet
    |> aggregate avg(total_rolling_bet) as avg_rolling_top_game_bet
        group by UserID, NewUserTag
)

from PlayerRepresentativeBet
|> extend
    percentile_cont(avg_rolling_top_game_bet, 0) over(partition by NewUserTag) as pr0,
    percentile_cont(avg_rolling_top_game_bet, 0.1) over(partition by NewUserTag) as pr10,
    percentile_cont(avg_rolling_top_game_bet, 0.2) over(partition by NewUserTag) as pr20,
    percentile_cont(avg_rolling_top_game_bet, 0.3) over(partition by NewUserTag) as pr30,
    percentile_cont(avg_rolling_top_game_bet, 0.4) over(partition by NewUserTag) as pr40,
    percentile_cont(avg_rolling_top_game_bet, 0.5) over(partition by NewUserTag) as pr50,
    percentile_cont(avg_rolling_top_game_bet, 0.6) over(partition by NewUserTag) as pr60,
    percentile_cont(avg_rolling_top_game_bet, 0.7) over(partition by NewUserTag) as pr70,
    percentile_cont(avg_rolling_top_game_bet, 0.8) over(partition by NewUserTag) as pr80,
    percentile_cont(avg_rolling_top_game_bet, 0.9) over(partition by NewUserTag) as pr90,
    percentile_cont(avg_rolling_top_game_bet, 1.0) over(partition by NewUserTag) as pr100
|> select distinct NewUserTag, pr0, pr10, pr20, pr30, pr40, pr50, pr60, pr70, pr80, pr90, pr100
|> unpivot (
    metric_value
    for metric_dim
    in(pr0, pr10, pr20, pr30, pr40, pr50, pr60, pr70, pr80, pr90, pr100)
)
;

# 全機台任務: 依照玩家在所有機台指定連續k天的平均表現
with DailyTotalBet as (
    from `rd7-data-big-query.bklog.SessionBetWinLog`
    |> where BQDate between 
                        date_sub(current_date('UTC+8'), interval recent_n_day day)
                        and date_sub(current_date('UTC+8'), interval 1 day)
            and Country = 'CN'
            and TotalBet > 0
    |> aggregate sum(TotalBet) as daily_total_bet
        group by UserID, BQDate
    |> extend extract(month from BQDate) as bet_month
    |> select UserID, BQDate, bet_month,daily_total_bet
)

, user_tag as (
    from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
    |> where BQDate >= date_trunc(date_sub(current_date('UTC+8'), interval recent_n_day day), month)
    |> extend extract(month from BQDate) as tag_month
    |> select tag_month, UserID, NewUserTag, UserTag
)

, tagged_DailyTopGameBet as (
    from DailyTotalBet dtb
    |> inner join user_tag ut
        on dtb.UserID = ut.UserID and dtb.bet_month = ut.tag_month
    |> select dtb.*, ut.NewUserTag
)

, RollingBet as (
    from tagged_DailyTopGameBet
    |> extend sum(daily_total_bet) over(
                                    partition by UserID, NewUserTag 
                                    order by unix_date(BQDate)
                                    range between 6 preceding and current row
                                 ) as total_rolling_bet
    |> select UserID, NewUserTag, total_rolling_bet
)

, PlayerRepresentativeBet as (
    from RollingBet
    |> aggregate avg(total_rolling_bet) as avg_rolling_top_game_bet
        group by UserID, NewUserTag
)

from PlayerRepresentativeBet
|> extend
    percentile_cont(avg_rolling_top_game_bet, 0) over(partition by NewUserTag) as pr0,
    percentile_cont(avg_rolling_top_game_bet, 0.1) over(partition by NewUserTag) as pr10,
    percentile_cont(avg_rolling_top_game_bet, 0.2) over(partition by NewUserTag) as pr20,
    percentile_cont(avg_rolling_top_game_bet, 0.3) over(partition by NewUserTag) as pr30,
    percentile_cont(avg_rolling_top_game_bet, 0.4) over(partition by NewUserTag) as pr40,
    percentile_cont(avg_rolling_top_game_bet, 0.5) over(partition by NewUserTag) as pr50,
    percentile_cont(avg_rolling_top_game_bet, 0.6) over(partition by NewUserTag) as pr60,
    percentile_cont(avg_rolling_top_game_bet, 0.7) over(partition by NewUserTag) as pr70,
    percentile_cont(avg_rolling_top_game_bet, 0.8) over(partition by NewUserTag) as pr80,
    percentile_cont(avg_rolling_top_game_bet, 0.9) over(partition by NewUserTag) as pr90,
    percentile_cont(avg_rolling_top_game_bet, 1.0) over(partition by NewUserTag) as pr100
|> select distinct NewUserTag, pr0, pr10, pr20, pr30, pr40, pr50, pr60, pr70, pr80, pr90, pr100
|> unpivot (
    metric_value
    for metric_dim
    in(pr0, pr10, pr20, pr30, pr40, pr50, pr60, pr70, pr80, pr90, pr100)
)
```

## [Rank] 已結算排行榜RTP檢核
**描述：** 用來看已經結算的排行榜每個人RTP與整體RTP

```sql
declare rank_settled_date date default '2026-03-10';
declare EventIDs array<string> default ['AR1772114505', 'AR1772114506', 'AR1772114507'];

with
  item_value as (
    from `rd7-data-big-query.DailyDimData.DailyDimItemValue`
    |> where BQDate >= rank_settled_date
    |> set ItemTypeID = concat('I', ItemTypeID)  
    |> select BQDate, ItemName, ItemTypeName, ItemTypeID, VipLevel, Value
  )

from `rd7-data-big-query.bklog.RankSettlementLog`
|> where BQDate >= rank_settled_date
    and EventID in unnest(EventIDs)
|> set RewardList = split(RewardList, ';')
|> select BQDate, 
          EventID, 
          UserID,
          VipLV, 
          Score, 
          Rank, 
          RewardList
|> cross join unnest(RewardList) as Reward
|> select * except(RewardList)
|> extend
    split(Reward, '_')[offset(0)] as reward_item,
    cast(split(Reward, '_')[offset(1)] as int64) as reward_count
|> as a   
|> left join item_value b
    on a.BQDate = b.BQDate and a.VipLV = b.VipLevel and a.reward_item = b.ItemTypeID
|> select a.*, b.ItemName, Value as reward_value
|> extend
    coalesce(reward_value, 1) * reward_count as Value
|> order by BQDate, Rank

# 計算每次排行榜的每人RTP 與 總RTP
|> aggregate
    sum(Value) total_value,
    any_value(Score) as score,
    round(sum(Value) / any_value(Score), 4) as personal_RTP
   group by BQDate, EventID, Rank, UserID
|> extend
    count(UserID) over(partition by EventID) as participant_counts,
    sum(total_value) over(partition by EventID) / sum(score) over(partition by EventID) as total_RTP
```

## [Rank] 設定檔排行榜資料處理
**描述：** 設定檔的資料進行清洗並整理欄位

```sql
# 定義要看的排行榜區間:幾號以後開、幾號以前結算
declare startdate date default '2026-03-01';
declare enddate date default '2026-03-31';

with 
# 設定檔資料準備
rank_data_0 as (
  from `rd7-data-big-query.bklog.DimActivityRankLog`
  |> where BQDate >= '2026-01-01' 
      and CountryOperation = 'and'
      and Country = 'CN'
      and IsGuild = 0
  |> set StartEventTime = DATE(TIMESTAMP_SECONDS(StartEventTime), 'Asia/Taipei'),
         LastEventTime = DATE(TIMESTAMP_SECONDS(LastEventTime), 'Asia/Taipei')
  |> where StartEventTime >= startdate and LastEventTime <= enddate
  |> extend 
      split(GID, '_')[offset(0)] as info1,
      split(GID, '_')[offset(1)] as info2,
      date_add(LastEventTime, interval 1 day) as settled_date,
      date_diff(LastEventTime, StartEventTime, day) as duration
  |> extend case when info1 = 'high' then 'slot' else 'fish' end as GameCategory
  |> select BQDate as setting_date, EventID, MainTab, SecondTab, GID, GameCategory, info1, info2, RankContent, Bet as bet_constraint, GameType, StartEventTime, LastEventTime, duration, settled_date, SwitchType
)

, deleted_rank as (
  from rank_data_0
  |> where SwitchType = -1
  |> select distinct EventID
) 

, rank_data_1 as (
  from rank_data_0
  |> where EventID not in (select * from deleted_rank)
)

, slot_rank_data as (
  from rank_data_1  a
  |> where GameCategory = 'slot'
  |> left join (select distinct GameID, GameName_CHT from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID`) b
      on a.info2 = cast(b.GameID as string)
  |> extend 'highroll' as c1
  |> rename GameName_CHT as c2
  |> select * except(GameID)
)

, fish_rank_data as (
  from rank_data_1 a
  |> where GameCategory = 'fish'
  |> left join (select distinct TableTypeIDCode, TableTypeIDName_TW from `rd7-data-big-query.MobileDW_Dragon.DimTableTypeID`) b
      on a.info1 = b.TableTypeIDCode
  |> left join (select distinct FishID, FishName_CHT from `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds`) c
      on a.info2 = cast(c.FishID as string)
  |> rename TableTypeIDName_TW as c1, FishName_CHT as c2
  |> select * except(TableTypeIDCode, FishID)
)

, all_rank_data as (
  (from slot_rank_data
  |> select setting_date, EventID, MainTab, SecondTab, GID, GameCategory, info1, info2, RankContent, bet_constraint, GameType, StartEventTime, LastEventTime, settled_date, c1, c2)
  
  union all
  
  (from fish_rank_data
  |> select setting_date, EventID, MainTab, SecondTab, GID, GameCategory, info1, info2, RankContent, bet_constraint, GameType, StartEventTime, LastEventTime, settled_date, c1, c2)
)
```

## [Rank] 排行榜總表分析
**描述：** 包含設定檔的排行榜資訊、結算資訊、RTP、押量增量資訊

```sql
5/10 更新

declare DS_START_DATE string default '20260401';
declare DS_END_DATE string default '20260430';
declare collectionrank_rtp float64 default 0.05;


with 
# ==========================================
# 1. 處理設定檔 (維度補充表)
# ==========================================
rank_config as (
  from `rd7-data-big-query.bklog.DimActivityRankLog`
  |> where BQDate between date_sub(PARSE_DATE('%Y%m%d', DS_START_DATE), interval 2 month) and PARSE_DATE('%Y%m%d', DS_END_DATE) # 排行榜通常是在開始日的前一個月內設定的，此處抓兩個月較保險
  |> extend 
      split(GID, '_')[safe_offset(0)] as info1,
      split(GID, '_')[safe_offset(1)] as info2,
  # 只要該 EventID 有出現過 -1 就整組排除
  |> where countif(SwitchType = -1) over(partition by EventID) = 0
  |> select distinct EventID, MainTab, SecondTab, GID, info1, info2, RankContent, Bet as bet_constraint, GameType, CountryOperation, Country
)

, slot_config as (
  from rank_config 
  |> where split(GameType, '_')[0] = 'S'
  |> extend 
      info1 as RankTargetGroup,
      info2 as join_var  # 用於串DailyGameMetric
  -- 第一步【展開 Fan-out】：將 "590,495" 拆成多行
  |> cross join unnest(split(info2, ',')) as single_game_id
  -- 第二步【關聯 Join】：這是標準的外部 JOIN
  |> left join (select distinct GameID, GameName_CHT from `rd7-data-big-query.MobileDW_Dragon.DimGame_ID`) dim
      on single_game_id = safe_cast(dim.GameID as string)
  -- 第三步【壓縮 Aggregate】：重新以 EventID 為單位包裝起來，並把名字串接
  |> aggregate
      -- 其他不需要變動的欄位，直接用 any_value 保留
      any_value(MainTab) as MainTab,
      any_value(SecondTab) as SecondTab,
      any_value(GID) as GID,
      any_value(RankContent) as RankContent,
      any_value(bet_constraint) as bet_constraint,
      any_value(GameType) as GameType,
      any_value(CountryOperation) as CountryOperation,
      any_value(Country) as Country,
      any_value(RankTargetGroup) as RankTargetGroup,
      string_agg(distinct dim.GameName_CHT, ', ') as RankTargetName,
      any_value(join_var) as join_var, 
     group by EventID
  |> extend 'None' as join_var2
)

, fish_config as (
  from rank_config 
  |> where split(GameType, '_')[0] = 'F'
  |> left join (select distinct TableTypeIDCode, TableTypeIDName_TW, TableTypeIDKey from `rd7-data-big-query.MobileDW_Dragon.DimTableTypeID`) b
      on info1 = b.TableTypeIDCode
  |> extend 
      b.TableTypeIDName_TW as RankTargetGroup,
      cast(b.TableTypeIDKey as string) as join_var,
      info2 as join_var2 # 用於串DailyUserFishMetric
  |> set join_var = case when join_var = '3' then '12,13,14' else join_var end
  -- ==========================================
  -- 開始處理 info2 (魚種名稱) 的一對多轉換
  -- ==========================================
  -- 第一步【展開】：將逗號分隔的魚種 ID 拆成多行
  |> cross join unnest(split(info2, ',')) as single_fish_id
  -- 第二步【關聯】：對接魚種維度表
  |> left join (
                select distinct FishID, FishName_CHT 
                from `rd7-data-big-query.MobileDW_Dragon.DimTigerSharkOdds` 
                qualify row_number() over(partition by FishID order by length(FishName_CHT) asc) = 1
               ) c
      on single_fish_id = safe_cast(c.FishID as string)
  -- 第三步【壓縮】：以 EventID 為單位重新打包，並合併魚種名稱
  |> aggregate
      any_value(MainTab) as MainTab,
      any_value(SecondTab) as SecondTab,
      any_value(GID) as GID,
      any_value(RankContent) as RankContent,
      any_value(bet_constraint) as bet_constraint,
      any_value(GameType) as GameType,
      any_value(CountryOperation) as CountryOperation,
      any_value(Country) as Country,
      any_value(RankTargetGroup) as RankTargetGroup,
      string_agg(distinct c.FishName_CHT, ', ') as RankTargetName,
      any_value(join_var) as join_var,
      any_value(join_var2) as join_var2
     group by EventID
)

, other_config as (
   from rank_config
   |> where split(GameType, '_')[0] not in ('S', 'F')
   |> select EventID, MainTab, SecondTab, GID, RankContent, bet_constraint, GameType, CountryOperation, Country, info1 as RankTargetGroup, info2 as RankTargetName, info2 as join_var, 'None' as join_var2
)


, all_rank_config as (
  (from slot_config |> select EventID, MainTab, SecondTab, GID, RankContent, bet_constraint, GameType,  CountryOperation, Country, RankTargetGroup, RankTargetName, join_var, join_var2)
  union all
  (from fish_config |> select  EventID, MainTab, SecondTab, GID, RankContent, bet_constraint, GameType,  CountryOperation, Country, RankTargetGroup, RankTargetName, join_var, join_var2)
  union all
  (from other_config |> select  EventID, MainTab, SecondTab, GID, RankContent, bet_constraint, GameType,  CountryOperation, Country, RankTargetGroup, RankTargetName, join_var, join_var2)
)
 
# ==========================================
# 2. 道具價值表: PK為BQDate + ItemTypeID + VipLevel
# ==========================================
, item_value as (
    from `rd7-data-big-query.DailyDimData.DailyDimItemValue` 
    |> where BQDate between PARSE_DATE('%Y%m%d', DS_START_DATE) and date_add(PARSE_DATE('%Y%m%d', DS_END_DATE), interval 1 day)
    |> aggregate 
          any_value(ItemName having max Value) as ItemName,
          max(Value) as item_unit_value
      group by BQDate, ItemTypeID, VipLevel
    |> extend concat('I', ItemTypeID) as I_ItemTypeID
    |> select BQDate, ItemTypeID, I_ItemTypeID, ItemName, VipLevel, item_unit_value
)

# ==========================================
# 3. UserID 的 Nickname(取排行榜設定window的最新) 跟 受眾(取排行榜結束時間當月)
# ==========================================
, user_info as (
  from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
  |> where BQDate between PARSE_DATE('%Y%m%d', DS_START_DATE) and PARSE_DATE('%Y%m%d', DS_END_DATE)
  |> select BQDate, UserID, NickName
  |> where  row_number() over(partition by UserID order by BQDate desc) = 1
  |> select UserID, NickName
)

, user_tag as (
  from `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
  |> where BQDate between date_trunc(PARSE_DATE('%Y%m%d', DS_START_DATE), month) and date_trunc(PARSE_DATE('%Y%m%d', DS_END_DATE), month)
  |> extend extract(month from BQDate) as tag_month
  |> select tag_month, UserID, NewUserTag, UserTag
)

# ==========================================
# 4. 【核心主表】結算紀錄轉換與計算
# ==========================================
, base_settlement_0 as (
  from `rd7-data-big-query.bklog.RankSettlementLog`
  |> where BQDate between PARSE_DATE('%Y%m%d', DS_START_DATE) and date_add(PARSE_DATE('%Y%m%d', DS_END_DATE), interval 1 day)
      and IsGuildRank = 0
  # 直接從排行榜結算紀錄解析出真正的活動開始與結束時間
  |> set 
      StartTime = DATETIME(TIMESTAMP_SECONDS(StartTime), 'Asia/Taipei'), 
      EndTime = DATETIME(TIMESTAMP_SECONDS(EndTime), 'Asia/Taipei')
  |> extend
      Date(StartTime) as StartDate,
      Date(EndTime) as EndDate
  |> where StartDate >= PARSE_DATE('%Y%m%d', DS_START_DATE) and EndDate <= PARSE_DATE('%Y%m%d', DS_END_DATE) 
  # 直接計算持續天數
  |> extend 
      div(datetime_diff(EndTime, StartTime, minute) + 1, 1440) as duration, # 1. datetime_diff 算出總分鐘差; 2. + 1 補齊 23:59:00 少掉的那 1 分鐘; 3. div(..., 1440) 強制無條件捨去取整數天 (1 天 = 1440 分鐘)
      (date_diff(EndDate, StartDate, day) + 1) as calendar_days, 
      case 
        when split(Type, '_')[0] = 'S' then 'Slot'
        when split(Type, '_')[0] = 'F' then 'Fish'
        when split(Type, '_')[0] = 'M' then 'Mahjong'
        when split(Type, '_')[0] = 'Pachi' then 'PachiSlot'
        when split(Type, '_')[0] = 'Horse' then 'Horse'
        when split(Type, '_')[0] = 'D' then 'Domino'
        when split(Type, '_')[0] = 'P' then
          case 
            when Type like '%Scratch%' then 'ScratchLottery'
            when Type like '%Collect%' then 'Collection'
          end  
        else split(Type, '_')[0]
      end as GameCategory
  |> rename BQDate as settled_date
)
  


, base_settlement as (
    (# 累積押分、贏分之排行榜直接取Score估押量 (因為有些排行榜會以小時區分來開，若join sessionlog會太大 join daily中轉表也是估而非精準)
     from base_settlement_0
     |> where (Type like '%Total%' and Type not like '%Times%')
     |> extend 
          Score as estimated_bet,
          'NA' as CollectionItemType_CHT
     |> select settled_date, EventID, StartTime, EndTime, StartDate, EndDate, duration, calendar_days, GameCategory, Type, CollectionItemType, CollectionItemType_CHT, Rank, RewardList, Score, UserID, VipLV, Country, estimated_bet
    )
    union all
    (# 估算收集物排行榜玩家押量
    from base_settlement_0
    |> where Type like '%Collect%'
    |> left join (
                  select BQDate, ItemTypeID, ItemName, max(item_unit_value) as max_item_unit_value
                  from item_value 
                  group by BQDate, ItemTypeID, ItemName
                  ) c
        on settled_date = c.BQDate and CollectionItemType = c.ItemTypeID
    |> extend 
        coalesce(c.ItemName, cast(CollectionItemType as string)) as CollectionItemType_CHT,
        Score * coalesce(c.max_item_unit_value, 0) / collectionrank_rtp as estimated_bet
    |> select settled_date, EventID, StartTime, EndTime, StartDate, EndDate, duration, calendar_days, GameCategory, Type, CollectionItemType, CollectionItemType_CHT, Rank, RewardList, Score, UserID, VipLV, Country, estimated_bet
    ) 
    union all
    (# 估算其他條件（次數...）之排行榜押量：非指定魚種排行榜
    from base_settlement_0
    |> where (Type not like '%Total%' or Type like '%Times%') and Type not like '%Collect%'
    |> extend 'NA' as CollectionItemType_CHT
    |> left join all_rank_config using(EventID)
    |> where join_var2 = 'None' or join_var2 is null 
    |> left join 
            (
            from `rd7-data-big-query.preprocessed_bklog.DailyUserGameMetrics`
            |> where BQDate between PARSE_DATE('%Y%m%d', DS_START_DATE) and PARSE_DATE('%Y%m%d', DS_END_DATE)
            |> extend 
                  split(GID, '_')[safe_offset(0)] as GameCategory,
                  split(GID, '_')[safe_offset(1)] as ProductID 
            |> select BQDate, UserID, GID, GameCategory, ProductID, CoinBet
            ) dugm
          on base_settlement_0.UserID = dugm.UserID 
            and dugm.BQDate between StartDate and EndDate 
            and base_settlement_0.GameCategory = dugm.GameCategory 
            and dugm.ProductID in unnest(split(join_var, ','))
    |> aggregate 
          any_value(settled_date) as settled_date,
          any_value(StartTime) as StartTime,
          any_value(EndTime) as EndTime,
          any_value(StartDate) as StartDate,
          any_value(EndDate) as EndDate,
          any_value(duration) as duration,
          any_value(calendar_days) as calendar_days,
          any_value(base_settlement_0.GameCategory) as GameCategory,
          any_value(Type) as Type,
          any_value(CollectionItemType) as CollectionItemType,
          any_value(CollectionItemType_CHT) as CollectionItemType_CHT,
          any_value(RewardList) as RewardList,
          any_value(Score) as Score,
          any_value(base_settlement_0.UserID) as UserID,
          any_value(VipLV) as VipLV,
          any_value(base_settlement_0.Country) as Country,
          coalesce(sum(dugm.CoinBet), -1) as estimated_bet
        group by EventID, Rank   
    |> select settled_date, EventID, StartTime, EndTime, StartDate, EndDate, duration, calendar_days, GameCategory, Type, CollectionItemType, CollectionItemType_CHT, Rank, RewardList, Score, UserID, VipLV, Country, estimated_bet
    )
    union all
    (# 估算其他條件（次數...）之排行榜押量：指定魚種排行榜
    from base_settlement_0
    |> where (Type not like '%Total%' or Type like '%Times%') and Type not like '%Collect%'
    |> extend 'NA' as CollectionItemType_CHT
    |> left join all_rank_config using(EventID)
    |> where join_var2 != 'None' and join_var2 is not null
    |> left join 
            (
            from `rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics`
            |> where BQDate between PARSE_DATE('%Y%m%d', DS_START_DATE) and PARSE_DATE('%Y%m%d', DS_END_DATE)
            |> aggregate sum(TotalBet) as TotalBet
                group by BQDate, UserID, TableTypeID, FishID, BetPerShoot
            |> select BQDate, UserID, cast(TableTypeID as string) as TableTypeID, cast(FishID as string) as FishID, BetPerShoot, TotalBet
            ) dufm
          on base_settlement_0.UserID = dufm.UserID 
            and dufm.BQDate between StartDate and EndDate 
            and dufm.BetPerShoot >= bet_constraint
            and dufm.TableTypeID in unnest(split(join_var, ','))
            and dufm.FishID in unnest(split(join_var2, ','))
    |> aggregate 
          any_value(settled_date) as settled_date,
          any_value(StartTime) as StartTime,
          any_value(EndTime) as EndTime,
          any_value(StartDate) as StartDate,
          any_value(EndDate) as EndDate,
          any_value(duration) as duration,
          any_value(calendar_days) as calendar_days,
          any_value(GameCategory) as GameCategory,
          any_value(Type) as Type,
          any_value(CollectionItemType) as CollectionItemType,
          any_value(CollectionItemType_CHT) as CollectionItemType_CHT,
          any_value(RewardList) as RewardList,
          any_value(Score) as Score,
          any_value(base_settlement_0.UserID) as UserID,
          any_value(VipLV) as VipLV,
          any_value(base_settlement_0.Country) as Country,
          coalesce(sum(dufm.TotalBet), -1) as estimated_bet
        group by EventID, Rank   
    |> select settled_date, EventID, StartTime, EndTime, StartDate, EndDate, duration, calendar_days, GameCategory, Type, CollectionItemType, CollectionItemType_CHT, Rank, RewardList, Score, UserID, VipLV, Country, estimated_bet
    )
      
  # 第二次 JOIN：展開與計算獎勵總值
  |> cross join unnest(split(RewardList, ';')) as Reward
  |> extend
      split(Reward, '_')[safe_offset(0)] as reward_item,
      safe_cast(split(Reward, '_')[safe_offset(1)] as int64) as reward_count
  |> left join item_value b
      on settled_date = b.BQDate and VipLV = b.VipLevel and reward_item = b.I_ItemTypeID 
  |> extend
      coalesce(b.item_unit_value, 1) * reward_count as total_reward_value_per_item,
      concat(coalesce(b.ItemName, reward_item), '*', safe_cast(reward_count as string)) as single_reward_string
  # 將展開的獎勵聚合回去，確保每人每榜只有一行
  |> aggregate
      any_value(StartTime) as StartTime,
      any_value(EndTime) as EndTime,
      any_value(StartDate) as StartDate,
      any_value(EndDate) as EndDate,
      any_value(duration) as duration,
      any_value(calendar_days) as calendar_days,
      any_value(GameCategory) as GameCategory,
      any_value(Type) as Type,
      any_value(CollectionItemType) as CollectionItemType,
      any_value(CollectionItemType_CHT) as CollectionItemType_CHT,
      any_value(Country) as winner_country,
      any_value(Score) as Score,
      any_value(estimated_bet) as estimated_bet,
      sum(total_reward_value_per_item) as final_total_reward_value,
      string_agg(single_reward_string, '; ') as FormattedRewardList
    group by settled_date, EventID, Rank, UserID
)

# ==========================================
# 5. 計算前後押量
# ==========================================
, user_bet_comparison as (
  from base_settlement r
  |> left join (
              select BQDate, UserID, SlotCoinBet, FishCoinBet, PachiSlotCoinBet, MahjongCoinBet, DominoCoinBet, ScratchLotteryCoinBet, BettingMachineCoinBet, CoinBet
              from `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
              where BQDate between date_sub(PARSE_DATE('%Y%m%d', DS_START_DATE), interval 30 day) and PARSE_DATE('%Y%m%d', DS_END_DATE)
              ) s 
      on r.UserID = s.UserID
        # 這裡改用 r.StartTime (結算表來的時間)，確保無設定檔也能匹配
        and s.BQDate between date_sub(r.StartDate, interval r.calendar_days day) and r.EndTime
  |> extend
      if(s.BQDate between r.StartDate and r.EndDate, 1, 0) as is_event_period,
      if(s.BQDate between date_sub(r.StartDate, interval r.calendar_days day) and date_sub(r.StartDate, interval 1 day), 1, 0) as is_pre_period
  |> aggregate 
      sum(if(is_pre_period = 1, coalesce(s.SlotCoinBet, 0), 0)) as pre_slot_bet,
      sum(if(is_pre_period = 1, coalesce(s.FishCoinBet, 0), 0)) as pre_fish_bet,
      sum(if(is_pre_period = 1, coalesce(s.PachiSlotCoinBet, 0), 0)) as pre_pachislot_bet,
      sum(if(is_pre_period = 1, coalesce(s.MahjongCoinBet, 0), 0)) as pre_mahjong_bet,
      sum(if(is_pre_period = 1, coalesce(s.DominoCoinBet, 0), 0)) as pre_domino_bet,
      sum(if(is_pre_period = 1, coalesce(s.ScratchLotteryCoinBet, 0), 0)) as pre_scratchlottery_bet,
      sum(if(is_pre_period = 1, coalesce(s.BettingMachineCoinBet, 0), 0)) as pre_bettingmachine_bet,
      sum(if(is_pre_period = 1, coalesce(s.CoinBet, 0), 0)) as pre_total_bet,

      sum(if(is_event_period = 1, coalesce(s.SlotCoinBet, 0), 0)) as event_slot_bet,
      sum(if(is_event_period = 1, coalesce(s.FishCoinBet, 0), 0)) as event_fish_bet,
      sum(if(is_event_period = 1, coalesce(s.PachiSlotCoinBet, 0), 0)) as event_pachislot_bet,
      sum(if(is_event_period = 1, coalesce(s.MahjongCoinBet, 0), 0)) as event_mahjong_bet,
      sum(if(is_event_period = 1, coalesce(s.DominoCoinBet, 0), 0)) as event_domino_bet,
      sum(if(is_event_period = 1, coalesce(s.ScratchLotteryCoinBet, 0), 0)) as event_scratchlottery_bet,
      sum(if(is_event_period = 1, coalesce(s.BettingMachineCoinBet, 0), 0)) as event_bettingmachine_bet,
      sum(if(is_event_period = 1, coalesce(s.CoinBet, 0), 0)) as event_total_bet,

      any_value(GameCategory) as GameCategory
     group by r.EventID, r.UserID
  |> extend
      case 
        when GameCategory = 'Slot' then pre_slot_bet 
        when GameCategory = 'Fish' then pre_fish_bet 
        when GameCategory = 'Mahjong' then pre_mahjong_bet 
        when GameCategory = 'PachiSlot' then pre_pachislot_bet 
        when GameCategory = 'Domino' then pre_domino_bet 
        when GameCategory = 'ScratchLottery' then pre_scratchlottery_bet 
        else null 
      end as pre_target_bet,
      
      case 
        when GameCategory = 'Slot' then event_slot_bet 
        when GameCategory = 'Fish' then event_fish_bet 
        when GameCategory = 'Mahjong' then event_mahjong_bet 
        when GameCategory = 'PachiSlot' then event_pachislot_bet 
        when GameCategory = 'Domino' then event_domino_bet 
        when GameCategory = 'ScratchLottery' then event_scratchlottery_bet 
        else null
      end as event_target_bet
  |> select * except(GameCategory)
)

# ==========================================
# 6. 最終產出：整合主表、補充維度與分析指標
# ==========================================
from base_settlement b
# a 為補充維度：因為目前設定檔的資料不包含M_TotalWin, M_TopNTotalWin, S_TopNDetailWin, P_CollectItemNameAmount, Pachi_TotalWonCoins條件排行榜，a 的欄位會自然呈現 Null，但不影響主幹計算
|> left join all_rank_config a using(EventID)
|> left join user_bet_comparison c using(EventID, UserID)
|> left join user_info d using(UserID)
|> left join user_tag e 
      on extract( month from b.EndTime) = e.tag_month and b.UserID = e.UserID
|> extend
      # 計算玩家層級的 RTP
      round(safe_divide(b.final_total_reward_value, b.estimated_bet), 4) as personal_RTP,
      # 計算增量
      c.event_total_bet - c.pre_total_bet as incremental_total_bet,
      c.event_target_bet - c.pre_target_bet as incremental_target_bet,
      safe_divide((c.event_total_bet - c.pre_total_bet), c.pre_total_bet) as total_bet_growth_rate,
      safe_divide((c.event_target_bet - c.pre_target_bet), c.pre_target_bet) as target_bet_growth_rate
|> select 
      b.EventID,
      b.settled_date,
      b.StartTime,
      b.EndTime,
      b.StartDate, 
      b.EndDate,
      b.duration,
      b.calendar_days,
      b.GameCategory, 
      b.Type,
      b.CollectionItemType,
      b.CollectionItemType_CHT,
      b.FormattedRewardList,
      b.Rank,
      b.UserID,
      d.NickName,
      e.UserTag,
      e.NewUserTag,
      b.winner_country,
      b.Score,
      b.estimated_bet,
      b.final_total_reward_value,
      a.MainTab,
      a.SecondTab,
      a.bet_constraint,
      a.CountryOperation, 
      a.Country,
      a.GID,
      a.RankTargetGroup,
      a.RankTargetName,
      a.RankContent,
      c.pre_slot_bet,
      c.pre_fish_bet,
      c.pre_pachislot_bet,
      c.pre_mahjong_bet,
      c.pre_domino_bet,
      c.pre_scratchlottery_bet,
      c.pre_bettingmachine_bet,
      c.pre_total_bet,
      c.event_slot_bet,
      c.event_fish_bet,
      c.event_pachislot_bet,
      c.event_mahjong_bet,
      c.event_domino_bet,
      c.event_scratchlottery_bet,
      c.event_bettingmachine_bet,
      c.event_total_bet,
      c.pre_target_bet,
      c.event_target_bet,
      personal_RTP,
      incremental_total_bet,
      incremental_target_bet,
      total_bet_growth_rate,
      target_bet_growth_rate
|> order by settled_date desc, EventID, Rank
;
```

## [Others] 每日總營收的來源
**描述：** 每天總營收是由哪些付費點組成

```sql
from `rd7-data-big-query.bklog.GameConsume`
|> where BQDate >= '2026-04-01'
      and Country = 'CN'
|> aggregate sum(BuyNumber) as TotalBuyNumber
    group by BQDate, SaleName
|> extend dense_rank() over(partition by BQDate order by TotalBuyNumber desc) as rank
|> where rank <= 5
|> order by BQDate, TotalBuyNumber desc
```

## [BattlePass] BP 免費線、付費線 發出獎勵狀況
**描述：** 檢驗每天的發出金幣量以及各個EventName發出輛

```sql
with missioninfo as (
  from `rd7-data-big-query.preprocessed_bklog.MissionList`
  |> where MissionStartDate >= '2026-04-15'
  |> select distinct EventName, MissionBookMark
)

# 5/1-5/5 BP付費線日均發出驟降
from `rd7-data-big-query.bklog.ActivityMissionRewardLog`
|> where BQDate between '2026-04-26' and '2026-05-05'
        and Country = 'CN'
        and RewardType = 1
        and BattlePass = 1
|> aggregate sum(RewardValue) as coin_distributed
    group by  BQDate, EventName
|> left join missioninfo using(EventName)
|> extend extract(month from BQDate) as month
|> select * except(EventName, BQDate)
|> pivot (
  sum(coin_distributed) as coin_distributed
  for month in (4, 5)
) 
|> set
    coin_distributed_4 = ifnull(coin_distributed_4, 0),
    coin_distributed_5 = ifnull(coin_distributed_5, 0)

|> extend coin_distributed_5 - coin_distributed_4 as diff
|> order by diff
```

## [BetStatus] 指定玩家在指定廳館的押量
**描述：** 查看魚機指定User 每天在指定廳館的押量，用於出專屬任務

```sql
# 不分押注段
from `rd7-data-big-query.preprocessed_bklog.DailyUserGameMetrics`
|> where BQDate between '2026-04-01' and '2026-05-07'
    and UserID = 58950363
    and split(GID, '_')[safe_offset(0)] = 'Fish'
    and split(GID, '_')[safe_offset(1)] in ('12', '13', '14')
|> aggregate  sum(CoinBet) as CoinBet, sum(CoinWin) as CoinWin, sum(CoinBetTimes) as CoinBetTimes
    group by BQDate

# 分押注段
from `rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics`
|> where BQDate between '2026-04-01' and '2026-05-07'
    and UserID = 58950363
    and TableTypeID in (12, 13, 14)
|> aggregate 
      sum(TotalWinTimes) as TotalWinTimes, 
      sum(TotalWin) as TotalWin,
      sum(TotalBetTimes) as TotalBetTotalBetTimes, 
      sum(TotalBet) as TotalBet
    group by BQDate, BetPerShoot
```
