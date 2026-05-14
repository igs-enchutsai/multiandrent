---
inclusion: always
---

# BigQuery 資料表 Schema（實際查詢結果）

查詢條件：BQDate = CURRENT_DATE('Asia/Taipei') - 1 day, LIMIT 100

成功：19 張表 | 失敗：0 張表


## `rd7-data-big-query.bklog.BattlePassBuyLog`
總行數約 8,332,708 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | NULLABLE |  |
| EventTime | INTEGER | NULLABLE | 事件發生時間 |
| UserID | INTEGER | NULLABLE | 玩家代號 |
| VipLV | INTEGER | NULLABLE | 玩家VIP等級 |
| Country | STRING | NULLABLE | 玩家國家 |
| BuyNumber | FLOAT | NULLABLE | 儲值金額 |
| VIPPointAwarded | INTEGER | NULLABLE | 獲得VP點數 |
| SystemType | INTEGER | NULLABLE | 系統類型 |
| BattlePassID | STRING | NULLABLE | Battle Pass ID |
| BuyResult | INTEGER | NULLABLE | 購買結果 |
| CoinAwarded | FLOAT | NULLABLE | 購買失敗獲得金幣 |
| OrderID | STRING | NULLABLE | 訂單編號 |

**Sample (5 rows):**
```
       BQDate   EventTime     UserID  VipLV Country  BuyNumber  VIPPointAwarded  SystemType                             BattlePassID  BuyResult  CoinAwarded     OrderID
0  2026-05-13  1778652338  107887791      2      AU       1.99                8           1  bp_SPF_LV2_20260513_10_v123456_exc_c...          1          0.0  P788889526
1  2026-05-13  1778652261  107887791      2      AU       0.99                4           1  bp_SPF_LV1_20260513_10_v123456_exc_c...          1          0.0  P788889498
2  2026-05-13  1778618340  101136582      3      JP       1.99                9           1  bp_CG_LV1_20260501_1000_v123456_exc_...          1          0.0  P788882763
3  2026-05-13  1778615616  104013649      3      JP       1.99                9           1  bp_CG_LV1_20260501_1000_v123456_exc_...          1          0.0  P788882403
4  2026-05-13  1778666095  104744092      3      JP       2.99               13           1  bp_CG_LV2_20260501_1000_v123456_exc_...          1          0.0  P788892898
```

## `rd7-data-big-query.bklog.ActivityMissionRewardLog`
總行數約 4,905,402,031 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| ProDate | INTEGER | NULLABLE |  |
| UserID | INTEGER | NULLABLE |  |
| MissionID | STRING | NULLABLE |  |
| EventTime | INTEGER | NULLABLE |  |
| VipLV | INTEGER | NULLABLE |  |
| Country | STRING | NULLABLE |  |
| EventName | STRING | NULLABLE |  |
| Reset | INTEGER | NULLABLE |  |
| PagePriority | INTEGER | NULLABLE |  |
| MissionPriority | INTEGER | NULLABLE |  |
| Difficulty | STRING | NULLABLE |  |
| Rule | STRING | NULLABLE |  |
| TargetTimes | INTEGER | NULLABLE |  |
| BatchID | STRING | NULLABLE |  |
| ActivityType | STRING | NULLABLE |  |
| AssignTab | STRING | NULLABLE |  |
| FrameType | INTEGER | NULLABLE |  |
| RewardType | INTEGER | NULLABLE |  |
| ItemType | INTEGER | NULLABLE |  |
| RewardValue | INTEGER | NULLABLE |  |
| BattlePass | INTEGER | NULLABLE |  |
| BalanceAfter | INTEGER | NULLABLE |  |
| MissionMode | INTEGER | NULLABLE |  |
| MissionBox | STRING | NULLABLE |  |
| LockType | INTEGER | NULLABLE |  |
| LockReason | INTEGER | NULLABLE |  |

**Sample (5 rows):**
```
       BQDate   ProDate     UserID                              MissionID   EventTime  VipLV Country                            EventName  Reset  PagePriority  MissionPriority Difficulty           Rule  TargetTimes           BatchID ActivityType AssignTab  FrameType  RewardType  ItemType  RewardValue  BattlePass  BalanceAfter  MissionMode MissionBox  LockType  LockReason
0  2026-05-13  20260513  107884062  EA_LV2_20260513_505_v23456_exc_cn_G_1  1778651073      2      KR  EA_LV2_20260513_505_v23456_exc_cn_G      0           505                0        LV2  slot_totalbet   1000000000  2026-05-01#3dccd           EA      None          1           4     92314           30           0            60            0       None         0           0
1  2026-05-13  20260513  107884062  EA_LV2_20260513_505_v23456_exc_cn_G_1  1778651073      2      KR  EA_LV2_20260513_505_v23456_exc_cn_G      0           505                0        LV2  slot_totalbet   1000000000  2026-05-01#3dccd           EA      None          1           4    400182            1           0             1            0       None         0           0
2  2026-05-13  20260513  107886929  EX_LV1_20260513_12_v123456_exc_cn_G_1  1778603763      2      VN  EX_LV1_20260513_12_v123456_exc_cn_G      0            12                0        LV1      pay_times            1  2026-05-01#2df33           EX      None          1           4    400190            1           0             1            0       None         0           0
3  2026-05-13  20260513  107886692  EX_LV1_20260513_12_v123456_exc_cn_G_1  1778601918      2      SG  EX_LV1_20260513_12_v123456_exc_cn_G      0            12                0        LV1      pay_times            1  2026-05-01#2df33           EX      None          1           4    400190            1           0             1            0       None         0           0
4  2026-05-13  20260513  107887012  EX_LV1_20260513_12_v123456_exc_cn_G_1  1778607158      2      VN  EX_LV1_20260513_12_v123456_exc_cn_G      0            12                0        LV1      pay_times            1  2026-05-01#2df33           EX      None          1           4    400190            1           0             1            0       None         0           0
```

## `rd7-data-big-query.bklog.ActivityMissionCompleteLog`
總行數約 2,851,971,921 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| UserID | INTEGER | NULLABLE | 玩家ID |
| MissionID | STRING | NULLABLE | 任務ID |
| EventTime | INTEGER | NULLABLE | 事件發生時間 |
| VipLV | INTEGER | NULLABLE | VIP等級 |
| Country | STRING | NULLABLE | 國家 |
| EventName | STRING | NULLABLE | 活動名稱 |
| StartTime | INTEGER | NULLABLE | 開始時間 |
| EndTime | INTEGER | NULLABLE | 結束時間 |
| CollectionItemType | INTEGER | NULLABLE | 收集的道具 |
| Reset | INTEGER | NULLABLE | 是否每日重致 |
| PagePriority | INTEGER | NULLABLE | 頁籤排序 |
| MissionPriority | INTEGER | NULLABLE | 任務排序 |
| Difficulty | STRING | NULLABLE | 難度 |
| Rule | STRING | NULLABLE | 任務類別 |
| TargetTimes | INTEGER | NULLABLE | 達成門檻 |
| BatchID | STRING | NULLABLE | 識別用ID |
| ActivityType | STRING | NULLABLE | 活動類別 |
| AssignTab | STRING | NULLABLE | 指定頁籤 |
| FrameType | INTEGER | NULLABLE | 是否是特殊操作 |
| MissionMode | INTEGER | NULLABLE | 任務類別 |
| MissionBox | STRING | NULLABLE | 任務收盒 |
| LockType | INTEGER | NULLABLE | 上鎖類別 |
| LockReason | INTEGER | NULLABLE | 上鎖原因 |

**Sample (5 rows):**
```
       BQDate     UserID                                MissionID   EventTime  VipLV Country                              EventName   StartTime     EndTime  CollectionItemType  Reset  PagePriority  MissionPriority Difficulty           Rule  TargetTimes            BatchID ActivityType AssignTab  FrameType  MissionMode MissionBox  LockType  LockReason
0  2026-05-13  107888096  DN_LV1_20260501_1000_v123456_exc_cn_G_1  1778676645      1      JP  DN_LV1_20260501_1000_v123456_exc_cn_G  1777564817  1780243140                  -1      0          1000                0        LV1  fish_totalwin     20000000  2025-05-01#f29714           DN      None          1            0       None         0           0
1  2026-05-13  107887791    EX_LV1_20260513_12_v123456_exc_cn_G_1  1778651686      1      AU    EX_LV1_20260513_12_v123456_exc_cn_G  1778601604  1778687940                  -1      0            12                0        LV1      pay_times            1   2026-05-01#2df33           EX      None          1            0       None         0           0
2  2026-05-13  107888347    EX_LV1_20260513_12_v123456_exc_cn_G_1  1778686508      1      JP    EX_LV1_20260513_12_v123456_exc_cn_G  1778601604  1778687940                  -1      0            12                0        LV1      pay_times            1   2026-05-01#2df33           EX      None          1            0       None         0           0
3  2026-05-13  107888433    EX_LV1_20260513_12_v123456_exc_cn_G_1  1778679116      1      JP    EX_LV1_20260513_12_v123456_exc_cn_G  1778601604  1778687940                  -1      0            12                0        LV1      pay_times            1   2026-05-01#2df33           EX      None          1            0       None         0           0
4  2026-05-13  107888691    EX_LV1_20260513_12_v123456_exc_cn_G_1  1778687431      1      JP    EX_LV1_20260513_12_v123456_exc_cn_G  1778601604  1778687940                  -1      0            12                0        LV1      pay_times            1   2026-05-01#2df33           EX      None          1            0       None         0           0
```

## `rd7-data-big-query.DailyDimData.ActivityMissionDimLog`
總行數約 29,139,035 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| Reset | INTEGER | NULLABLE |  |
| MissionBookMark | STRING | NULLABLE |  |
| MissionID | STRING | NULLABLE |  |
| MissionPriority | INTEGER | NULLABLE |  |
| ActivityType | STRING | NULLABLE |  |
| PagePriority | INTEGER | NULLABLE |  |
| MissionName | STRING | NULLABLE |  |
| Rule | STRING | NULLABLE |  |
| TargetTimes | INTEGER | NULLABLE |  |
| VipLV | INTEGER | NULLABLE |  |
| MissionValue | INTEGER | NULLABLE |  |
| BPMissionValue | INTEGER | NULLABLE |  |
| AssignTab | STRING | NULLABLE |  |
| FrameType | INTEGER | NULLABLE |  |
| ActivityStartTime | DATE | NULLABLE |  |
| ActivityEndTime | DATE | NULLABLE |  |
| MissionFeature | STRING | NULLABLE |  |
| InGameMissionBookMark | STRING | NULLABLE |  |
| BatchID | STRING | NULLABLE |  |
| PlayerTags | STRING | NULLABLE |  |
| Operation | STRING | NULLABLE |  |
| ActivityGameID | STRING | NULLABLE |  |
| GameType | STRING | NULLABLE |  |
| GameCategory | STRING | NULLABLE |  |
| BufferRate_Free | FLOAT | NULLABLE |  |
| BufferRate_Pay | FLOAT | NULLABLE |  |
| RunDay | INTEGER | NULLABLE |  |
| BreakDay | INTEGER | NULLABLE |  |
| CountryOperation | STRING | NULLABLE |  |
| Country | STRING | NULLABLE |  |
| MissionCardValue | INTEGER | NULLABLE |  |
| BPMissionCardValue | INTEGER | NULLABLE |  |
| BattlePassBuyNumber | FLOAT | NULLABLE |  |
| MissionFeatureCHT | STRING | NULLABLE |  |
| EventName | STRING | NULLABLE |  |
| FreeAwardType | INTEGER | NULLABLE |  |
| BuyAwardType | INTEGER | NULLABLE |  |
| BatchIDTs | INTEGER | NULLABLE |  |
| MissionReward | STRING | NULLABLE |  |
| BPMissionReward | STRING | NULLABLE |  |
| AppendRule | STRING | NULLABLE |  |

**Sample (5 rows):**
```
       BQDate  Reset                   MissionBookMark                            MissionID  MissionPriority ActivityType  PagePriority                    MissionName                Rule  TargetTimes  VipLV  MissionValue  BPMissionValue AssignTab  FrameType ActivityStartTime ActivityEndTime MissionFeature InGameMissionBookMark           BatchID PlayerTags Operation ActivityGameID GameType GameCategory  BufferRate_Free  BufferRate_Pay  RunDay  BreakDay CountryOperation Country  MissionCardValue  BPMissionCardValue  BattlePassBuyNumber MissionFeatureCHT                          EventName  FreeAwardType  BuyAwardType   BatchIDTs   MissionReward                 BPMissionReward                               AppendRule
0  2026-05-13      0  指定廳館_0_0_魚_入門館_1天_25_2_15_0_三隻小豬  F_LV2_20260513_70_v23456_for_my_G_1                1            F            70  入門館 押注20,000以上 三隻小豬 累積吹垮茅草屋3間  f_collect_activity            3      2       1000000         3772277                    1        2026-05-13      2026-05-31             AS               三隻小豬-挑戰  2026-05-13#7c0ca                                None     fish         酒霸狂鯊             50.0             0.0       1         0              for      MY           1000000             3172277                 0.99            新魚主題活動  F_LV2_20260513_70_v23456_for_my_G              4             2  1778590644  {"I400185": 1}  {"coin": 600000, "I400140": 1}  {"modename": "ThePigHouse", "custome...
1  2026-05-13      0  指定廳館_0_0_魚_入門館_1天_25_2_15_0_三隻小豬  F_LV2_20260513_70_v23456_for_my_G_1                1            F            70  入門館 押注20,000以上 三隻小豬 累積吹垮茅草屋3間  f_collect_activity            3      3       1000000         3772277                    1        2026-05-13      2026-05-31             AS               三隻小豬-挑戰  2026-05-13#7c0ca                                None     fish         酒霸狂鯊             50.0             0.0       1         0              for      MY           1000000             3172277                 0.99            新魚主題活動  F_LV2_20260513_70_v23456_for_my_G              4             2  1778590644  {"I400185": 1}  {"coin": 600000, "I400140": 1}  {"modename": "ThePigHouse", "custome...
2  2026-05-13      0  指定廳館_0_0_魚_入門館_1天_25_2_15_0_三隻小豬  F_LV2_20260513_70_v23456_for_my_G_1                1            F            70  入門館 押注20,000以上 三隻小豬 累積吹垮茅草屋3間  f_collect_activity            3      4       1000000         3772277                    1        2026-05-13      2026-05-31             AS               三隻小豬-挑戰  2026-05-13#7c0ca                                None     fish         酒霸狂鯊             50.0             0.0       1         0              for      MY           1000000             3172277                 0.99            新魚主題活動  F_LV2_20260513_70_v23456_for_my_G              4             2  1778590644  {"I400185": 1}  {"coin": 600000, "I400140": 1}  {"modename": "ThePigHouse", "custome...
3  2026-05-13      0  指定廳館_0_0_魚_入門館_1天_25_2_15_0_三隻小豬  F_LV2_20260513_70_v23456_for_my_G_1                1            F            70  入門館 押注20,000以上 三隻小豬 累積吹垮茅草屋3間  f_collect_activity            3      5       1000000         3772277                    1        2026-05-13      2026-05-31             AS               三隻小豬-挑戰  2026-05-13#7c0ca                                None     fish         酒霸狂鯊             50.0             0.0       1         0              for      MY           1000000             3172277                 0.99            新魚主題活動  F_LV2_20260513_70_v23456_for_my_G              4             2  1778590644  {"I400185": 1}  {"coin": 600000, "I400140": 1}  {"modename": "ThePigHouse", "custome...
4  2026-05-13      0  指定廳館_0_0_魚_入門館_1天_25_2_15_0_三隻小豬  F_LV2_20260513_70_v23456_for_my_G_1                1            F            70  入門館 押注20,000以上 三隻小豬 累積吹垮茅草屋3間  f_collect_activity            3      6       1000000         3772277                    1        2026-05-13      2026-05-31             AS               三隻小豬-挑戰  2026-05-13#7c0ca                                None     fish         酒霸狂鯊             50.0             0.0       1         0              for      MY           1000000             3172277                 0.99            新魚主題活動  F_LV2_20260513_70_v23456_for_my_G              4             2  1778590644  {"I400185": 1}  {"coin": 600000, "I400140": 1}  {"modename": "ThePigHouse", "custome...
```

## `rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot`
總行數約 244,799,810 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| UserID | INTEGER | NULLABLE |  |
| Country | STRING | NULLABLE |  |
| CountryDetail | STRING | NULLABLE |  |
| VipLV | INTEGER | NULLABLE |  |
| CreateDate | DATE | NULLABLE |  |
| GameLevel | INTEGER | NULLABLE |  |
| NickName | STRING | NULLABLE |  |
| Email | STRING | NULLABLE |  |
| Status | INTEGER | REPEATED |  |
| GuildID | STRING | NULLABLE |  |
| GuildName | STRING | NULLABLE |  |
| CoinAwarded | FLOAT | NULLABLE |  |
| GemAwarded | INTEGER | NULLABLE |  |
| TotalCoinAwarded | FLOAT | NULLABLE |  |
| CoinConsumed | FLOAT | NULLABLE |  |
| GemConsumed | INTEGER | NULLABLE |  |
| TotalCoinConsumed | FLOAT | NULLABLE |  |
| Coin | INTEGER | NULLABLE |  |
| Gem | INTEGER | NULLABLE |  |
| EndBalance | INTEGER | NULLABLE |  |
| TotalCoinSent | FLOAT | NULLABLE |  |
| CoinSentToBlackDiamond | FLOAT | NULLABLE |  |
| CoinSentToNormal | FLOAT | NULLABLE |  |
| TotalCoinReceived | FLOAT | NULLABLE |  |
| CoinReceivedFromBlackDiamond | FLOAT | NULLABLE |  |
| CoinReceivedFromNormal | FLOAT | NULLABLE |  |
| BuyNumber | FLOAT | NULLABLE |  |
| LastVisitDate | DATE | NULLABLE |  |
| UserType | STRING | NULLABLE |  |
| LastBuyDate | DATE | NULLABLE |  |
| ThirdPartyType | INTEGER | NULLABLE |  |
| InstallSource | STRING | NULLABLE |  |
| InstallDate | DATE | NULLABLE |  |
| Channel | INTEGER | NULLABLE |  |
| BlackDiamondTag | STRING | NULLABLE |  |
| FishCoinBet | INTEGER | NULLABLE |  |
| FishCoinWin | INTEGER | NULLABLE |  |
| FishCoinRet | INTEGER | NULLABLE |  |
| FishCoinBetTimes | INTEGER | NULLABLE |  |
| FishNormalCoinBet | INTEGER | NULLABLE |  |
| FishNormalCoinWin | INTEGER | NULLABLE |  |
| FishNormalCoinRet | INTEGER | NULLABLE |  |
| FishNormalCoinBetTimes | INTEGER | NULLABLE |  |
| FishVIPCoinBet | INTEGER | NULLABLE |  |
| FishVIPCoinWin | INTEGER | NULLABLE |  |
| FishVIPCoinRet | INTEGER | NULLABLE |  |
| FishVIPCoinBetTimes | INTEGER | NULLABLE |  |
| FishRookieCoinBet | INTEGER | NULLABLE |  |
| FishRookieCoinWin | INTEGER | NULLABLE |  |
| FishRookieCoinRet | INTEGER | NULLABLE |  |
| FishRookieCoinBetTimes | INTEGER | NULLABLE |  |
| FishDinoCoinBet | INTEGER | NULLABLE |  |
| FishDinoCoinWin | INTEGER | NULLABLE |  |
| FishDinoCoinRet | INTEGER | NULLABLE |  |
| FishDinoCoinBetTimes | INTEGER | NULLABLE |  |
| FishPhoenixCoinBet | INTEGER | NULLABLE |  |
| FishPhoenixCoinWin | INTEGER | NULLABLE |  |
| FishPhoenixCoinRet | INTEGER | NULLABLE |  |
| FishPhoenixCoinBetTimes | INTEGER | NULLABLE |  |
| FishZombieCoinBet | INTEGER | NULLABLE |  |
| FishZombieCoinWin | INTEGER | NULLABLE |  |
| FishZombieCoinRet | INTEGER | NULLABLE |  |
| FishZombieCoinBetTimes | INTEGER | NULLABLE |  |
| FishJurasCoinBet | INTEGER | NULLABLE |  |
| FishJurasCoinWin | INTEGER | NULLABLE |  |
| FishJurasCoinRet | INTEGER | NULLABLE |  |
| FishJurasCoinBetTimes | INTEGER | NULLABLE |  |
| SlotCoinBet | INTEGER | NULLABLE |  |
| SlotCoinWin | INTEGER | NULLABLE |  |
| SlotCoinRet | INTEGER | NULLABLE |  |
| SlotCoinBetTimes | INTEGER | NULLABLE |  |
| PachiSlotCoinBet | INTEGER | NULLABLE |  |
| PachiSlotCoinWin | INTEGER | NULLABLE |  |
| PachiSlotCoinRet | INTEGER | NULLABLE |  |
| PachiSlotCoinBetTimes | INTEGER | NULLABLE |  |
| MahjongCoinBet | INTEGER | NULLABLE |  |
| MahjongCoinWin | INTEGER | NULLABLE |  |
| MahjongCoinRet | INTEGER | NULLABLE |  |
| MahjongCoinBetTimes | INTEGER | NULLABLE |  |
| DominoCoinBet | INTEGER | NULLABLE |  |
| DominoCoinWin | INTEGER | NULLABLE |  |
| DominoCoinRet | INTEGER | NULLABLE |  |
| DominoCoinBetTimes | INTEGER | NULLABLE |  |
| ScratchLotteryCoinBet | INTEGER | NULLABLE |  |
| ScratchLotteryCoinWin | INTEGER | NULLABLE |  |
| ScratchLotteryCoinRet | INTEGER | NULLABLE |  |
| ScratchLotteryCoinBetTimes | INTEGER | NULLABLE |  |
| BettingMachineCoinBet | INTEGER | NULLABLE |  |
| BettingMachineCoinWin | INTEGER | NULLABLE |  |
| BettingMachineCoinRet | INTEGER | NULLABLE |  |
| BettingMachineCoinBetTimes | INTEGER | NULLABLE |  |
| CoinBet | INTEGER | NULLABLE |  |
| CoinWin | INTEGER | NULLABLE |  |
| CoinRet | INTEGER | NULLABLE |  |
| CoinBetTimes | INTEGER | NULLABLE |  |
| FreeBPCoinAwarded | INTEGER | NULLABLE |  |
| BuyBPCoinAwarded | INTEGER | NULLABLE |  |
| BPBuyNumber | FLOAT | NULLABLE |  |
| RiskLevel | STRING | NULLABLE |  |
| SysType | STRING | NULLABLE |  |
| FishVIPMythCoinBet | INTEGER | NULLABLE |  |
| FishVIPMythCoinWin | INTEGER | NULLABLE |  |
| FishVIPMythCoinRet | INTEGER | NULLABLE |  |
| FishVIPMythCoinBetTimes | INTEGER | NULLABLE |  |
| FishVIPMechCoinBet | INTEGER | NULLABLE |  |
| FishVIPMechCoinWin | INTEGER | NULLABLE |  |
| FishVIPMechCoinRet | INTEGER | NULLABLE |  |
| FishVIPMechCoinBetTimes | INTEGER | NULLABLE |  |
| FishVIPLuckCoinBet | INTEGER | NULLABLE |  |
| FishVIPLuckCoinWin | INTEGER | NULLABLE |  |
| FishVIPLuckCoinRet | INTEGER | NULLABLE |  |
| FishVIPLuckCoinBetTimes | INTEGER | NULLABLE |  |
| IsCoinChanged | INTEGER | NULLABLE |  |
| BaseSlotNBufferWin | FLOAT | NULLABLE |  |
| EventSlotNBufferWin | FLOAT | NULLABLE |  |
| GameBufferSlotNBufferWin | FLOAT | NULLABLE |  |
| RealNameID | STRING | NULLABLE |  |

**Sample (5 rows):**
```
       BQDate     UserID Country CountryDetail  VipLV  CreateDate  GameLevel   NickName Email                                   Status GuildID GuildName  CoinAwarded  GemAwarded  TotalCoinAwarded  CoinConsumed  GemConsumed  TotalCoinConsumed     Coin  Gem  EndBalance  TotalCoinSent  CoinSentToBlackDiamond  CoinSentToNormal  TotalCoinReceived  CoinReceivedFromBlackDiamond  CoinReceivedFromNormal  BuyNumber LastVisitDate UserType LastBuyDate  ThirdPartyType InstallSource InstallDate  Channel BlackDiamondTag  FishCoinBet  FishCoinWin  FishCoinRet  FishCoinBetTimes  FishNormalCoinBet  FishNormalCoinWin  FishNormalCoinRet  FishNormalCoinBetTimes  FishVIPCoinBet  FishVIPCoinWin  FishVIPCoinRet  FishVIPCoinBetTimes  FishRookieCoinBet  FishRookieCoinWin  FishRookieCoinRet  FishRookieCoinBetTimes  FishDinoCoinBet  FishDinoCoinWin  FishDinoCoinRet  FishDinoCoinBetTimes  FishPhoenixCoinBet  FishPhoenixCoinWin  FishPhoenixCoinRet  FishPhoenixCoinBetTimes  FishZombieCoinBet  FishZombieCoinWin  FishZombieCoinRet  FishZombieCoinBetTimes  FishJurasCoinBet  FishJurasCoinWin  FishJurasCoinRet  FishJurasCoinBetTimes  SlotCoinBet  SlotCoinWin  SlotCoinRet  SlotCoinBetTimes  PachiSlotCoinBet  PachiSlotCoinWin  PachiSlotCoinRet  PachiSlotCoinBetTimes  MahjongCoinBet  MahjongCoinWin  MahjongCoinRet  MahjongCoinBetTimes  DominoCoinBet  DominoCoinWin  DominoCoinRet  DominoCoinBetTimes  ScratchLotteryCoinBet  ScratchLotteryCoinWin  ScratchLotteryCoinRet  ScratchLotteryCoinBetTimes  BettingMachineCoinBet  BettingMachineCoinWin  BettingMachineCoinRet  BettingMachineCoinBetTimes  CoinBet  CoinWin  CoinRet  CoinBetTimes  FreeBPCoinAwarded  BuyBPCoinAwarded  BPBuyNumber RiskLevel SysType  FishVIPMythCoinBet  FishVIPMythCoinWin  FishVIPMythCoinRet  FishVIPMythCoinBetTimes  FishVIPMechCoinBet  FishVIPMechCoinWin  FishVIPMechCoinRet  FishVIPMechCoinBetTimes  FishVIPLuckCoinBet  FishVIPLuckCoinWin  FishVIPLuckCoinRet  FishVIPLuckCoinBetTimes  IsCoinChanged  BaseSlotNBufferWin  EventSlotNBufferWin  GameBufferSlotNBufferWin RealNameID
0  2026-05-13  107888751  Others            MY      1  2026-05-13          1  107888751  None                                       []    None      None    1000000.0           0         1000000.0           0.0            0                0.0  1000000    0     1000000            0.0                     0.0               0.0                0.0                           0.0                     0.0        0.0           NaT       新進         NaT               6       Unknown  2026-05-13        2              一般            0            0            0                 0                  0                  0                  0                       0               0               0               0                    0                  0                  0                  0                       0                0                0                0                     0                   0                   0                   0                        0                  0                  0                  0                       0                 0                 0                 0                      0            0            0            0                 0                 0                 0                 0                      0               0               0               0                    0              0              0              0                   0                      0                      0                      0                           0                      0                      0                      0                           0        0        0        0             0                  0                 0          0.0       無風險       1                   0                   0                   0                        0                   0                   0                   0                        0                   0                   0                   0                        0              1                 0.0                  0.0                       0.0       None
1  2026-05-13   62579024      CN            CN      1  2021-12-21        165   62579024  None  [35, 162, 172, 223, 231, 505, 9047, ...    None      None     193400.0           0          193400.0       33500.0            0            33500.0  3461872    0     3461872            0.0                     0.0               0.0                0.0                           0.0                     0.0        0.0    2026-05-12    30日活躍         NaT               5       Unknown  2021-12-21        1              一般      1751500      1718000        33500              3501                  0                  0                  0                       0               0               0               0                    0                  0                  0                  0                       0                0                0                0                     0                   0                   0                   0                        0                  0                  0                  0                       0                 0                 0                 0                      0            0            0            0                 0                 0                 0                 0                      0               0               0               0                    0              0              0              0                   0                      0                      0                      0                           0                      0                      0                      0                           0  1751500  1718000    33500          3501                  0                 0          0.0       無風險       1                   0                   0                   0                        0                   0                   0                   0                        0                   0                   0                   0                        0              1                 0.0                  0.0                       0.0       None
2  2026-05-13   61920820      CN            CN      2  2021-12-08        168   61920820  None  [35, 162, 172, 221, 222, 231, 507, 9...    None      None     150300.0           0          150300.0       25500.0            0            25500.0  4264443    0     4264443            0.0                     0.0               0.0                0.0                           0.0                     0.0        0.0    2026-05-12    30日活躍  2025-11-18               5       Unknown  2021-12-08        1              一般      2392500      2367000        25500              4782                  0                  0                  0                       0               0               0               0                    0                  0                  0                  0                       0                0                0                0                     0                   0                   0                   0                        0                  0                  0                  0                       0                 0                 0                 0                      0            0            0            0                 0                 0                 0                 0                      0               0               0               0                    0              0              0              0                   0                      0                      0                      0                           0                      0                      0                      0                           0  2392500  2367000    25500          4782                  0                 0          0.0       無風險       1                   0                   0                   0                        0                   0                   0                   0                        0                   0                   0                   0                        0              1                 0.0                  0.0                       0.0       None
3  2026-05-13  107649266  Others            PH      1  2026-02-09         32  107649266  None                           [60002, 89771]    None      None          0.0           0               0.0           0.0            0                0.0  5406059    0     5406059            0.0                     0.0               0.0                0.0                           0.0                     0.0        0.0           NaT    30日回流         NaT               6       Unknown  2026-02-09        2              一般            0            0            0                 0                  0                  0                  0                       0               0               0               0                    0                  0                  0                  0                       0                0                0                0                     0                   0                   0                   0                        0                  0                  0                  0                       0                 0                 0                 0                      0            0            0            0                 0                 0                 0                 0                      0               0               0               0                    0              0              0              0                   0                      0                      0                      0                           0                      0                      0                      0                           0        0        0        0             0                  0                 0          0.0       無風險       1                   0                   0                   0                        0                   0                   0                   0                        0                   0                   0                   0                        0              1                 0.0                  0.0                       0.0       None
4  2026-05-13   60054463      CN            CN      3  2021-10-22        404        李逍遥  None  [35, 141, 163, 172, 192, 202, 221, 2...    None      None     821500.0           0          821500.0      900000.0            0           900000.0    15764    3       90764            0.0                     0.0               0.0           400000.0                           0.0                400000.0        0.0    2026-05-12    30日活躍         NaT               5  unityads_int  2021-10-22     1062              一般            0            0            0                 0                  0                  0                  0                       0               0               0               0                    0                  0                  0                  0                       0                0                0                0                     0                   0                   0                   0                        0                  0                  0                  0                       0                 0                 0                 0                      0      1050000       150000       900000                28                 0                 0                 0                      0               0               0               0                    0              0              0              0                   0                      0                      0                      0                           0                      0                      0                      0                           0  1050000   150000   900000            28               2000                 0          0.0       無風險       1                   0                   0                   0                        0                   0                   0                   0                        0                   0                   0                   0                        0              1             37500.0              75000.0                   75000.0       None
```

## `rd7-data-big-query.bklog.SessionActive`
總行數約 1,448,859,281 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| ProDate | INTEGER | NULLABLE | 資料傳送日期 |
| LoginDate | INTEGER | NULLABLE | 登入日期 |
| SessionID | STRING | NULLABLE | SessionID |
| UserID | INTEGER | NULLABLE | 玩家自動ID(帳號) |
| LoginTime | INTEGER | NULLABLE | 登入時間 |
| UDID | STRING | NULLABLE | 設備識別ID |
| SysType | INTEGER | NULLABLE | 
操作系統 |
| Country | STRING | NULLABLE | 所在地區(國別) |
| Region | STRING | NULLABLE | 所在地區(省市) |
| Channel | INTEGER | NULLABLE | 上架平台/渠道 |
| PublishVer | STRING | NULLABLE | 遊戲版本 |
| DEV | STRING | NULLABLE | 機型 |
| SysVer | STRING | NULLABLE | 操作系統版本 |
| Resolution | STRING | NULLABLE | 解析度/分辨率 |
| Network | INTEGER | NULLABLE | 聯網方式 |
| LV | INTEGER | NULLABLE | 目前等級 |
| VipLV | INTEGER | NULLABLE | 目前VIP等級 |
| LoginTimeTs | INTEGER | NULLABLE | 登入時間 10位數 |
| TimeZone | FLOAT | NULLABLE | 時區彌補時數 |
| CurrChannel | INTEGER | NULLABLE | 玩家登入的渠道 |
| IP | STRING | NULLABLE | 玩家登入IP |
| AAID | STRING | NULLABLE | AAID |
| IDFA | STRING | NULLABLE | IDFA |
| IDFV | STRING | NULLABLE | IDFV |
| IMEI | STRING | NULLABLE | IMEI |
| AndroidID | STRING | NULLABLE | AndroidID |
| ThirdPartyType | INTEGER | NULLABLE | 第三方验证登入平台 |
| LoginCountry | STRING | NULLABLE | 登入國家 |
| RealDevice | INTEGER | NULLABLE | 是否為真實裝置 |

**Sample (5 rows):**
```
       BQDate   ProDate  LoginDate                         SessionID     UserID         LoginTime              UDID  SysType Country     Region  Channel PublishVer                DEV                SysVer Resolution  Network   LV  VipLV  LoginTimeTs  TimeZone  CurrChannel              IP                              AAID  IDFA  IDFV             IMEI         AndroidID  ThirdPartyType LoginCountry  RealDevice
0  2026-05-13  20260513   20260513  2c97ca9f0c53ea1bf8829bd17f2d5506  107888751  1778687962581060  38e69373f713a768        1      MY       None        2      4.5.6  Xiaomi 24094RAD4G  Android OS 16 / API-  2400x1080        0    1      1   1778687962       8.0            2    182.62.183.7  b0ae27790e574c0fa9d349645e906863  None  None             None  38e69373f713a768               6           MY           1
1  2026-05-13  20260513   20260513  09664f4bef4f219318d0661f71d9fc9f   62360034  1778656886303832   861340842811557        1      CN  Guangzhou        1    4.5.0.3       360 1509-A00  Android OS 5.1.1 / A  1920x1080        5  155      1   1778656886       8.0           13   101.82.88.180                              None  None  None  861340842811557              None               5           CN           1
2  2026-05-13  20260513   20260513  2a5d1f2d022258d863c6d2150ee18ae8   62796557  1778668826864654   864715153289595        1      CN     Huzhou        1    4.5.0.3       360 1509-A00  Android OS 4.4.w / A  1920x1080        1   77      1   1778668826       8.0           13  106.111.99.181                              None  None  None  864715153289595              None               5           CN           1
3  2026-05-13  20260513   20260513  411448b4de673f3643458ec703f028c3   48066557  1778679856336364   864406072496532        1      CN  Guangzhou        1    4.5.0.3       360 1509-A00  Android OS 4.4.w / A  1920x1080        2  150      1   1778679856       8.0           13  110.82.241.232                              None  None  None  864406072496532              None               5           CN           1
4  2026-05-13  20260513   20260513  54262b48ee87c24fe38c12c46f5edad8   61889846  1778616410331732   867956653515312        1      CN   Shanghai        1    4.5.0.3       360 1509-A00  Android OS 6.0.1 / A  1920x1080        1  141      1   1778616410       8.0           13    110.84.200.8                              None  None  None  867956653515312              None               5           CN           1
```

## `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`
總行數約 4,887,860,602 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| SessionID | STRING | NULLABLE | SessionID |
| StartEventTime | INTEGER | NULLABLE | 第一次紀錄時間 |
| LastEventTime | INTEGER | NULLABLE | 最後一次紀錄時間 |
| UserID | INTEGER | NULLABLE | 玩家ID |
| BetPerShoot | INTEGER | NULLABLE | 單次射擊Bet值 |
| QualifyForJP | INTEGER | NULLABLE | 是否參與JP |
| BetID | INTEGER | NULLABLE | Bet ID |
| TotalBetTimes | INTEGER | NULLABLE | 總Bet次數 |
| TotalBet | FLOAT | NULLABLE | 總押注額 |
| TotalWinTimes | INTEGER | NULLABLE | 總Win次數 |
| TotalWin | FLOAT | NULLABLE | 總贏分 |
| EndBalance | FLOAT | NULLABLE | session結束時的玩家餘額 |
| UDID | STRING | NULLABLE | 設備識別ID |
| TableTypeID | INTEGER | NULLABLE | 廳館ID |
| LV | INTEGER | NULLABLE | Level |
| VipLV | INTEGER | NULLABLE | VIP Level |
| SessionName | STRING | NULLABLE | 排行榜ID |
| StartBalance | FLOAT | NULLABLE | session進入時的玩家餘額 |
| Country | STRING | NULLABLE | 所在地區(國別) |
| TotalJPWin | FLOAT | NULLABLE | 參與JP所獲金錢 |
| StartBuffer | INTEGER | NULLABLE | session進入時的buffer值 |
| EndBuffer | INTEGER | NULLABLE | session結束時的buffer值 |
| CutBuffer | INTEGER | NULLABLE | 砍掉buffer值 |
| TotalCardTimes | INTEGER | NULLABLE | 武器卡使用次數 |
| TotalCardWin | INTEGER | NULLABLE | 武器卡所獲金錢 |
| TotalRepayWin | FLOAT | NULLABLE | 斷線補償置獎金額 |
| ClientVersion | STRING | NULLABLE | 玩家版本 |
| CoinGroup | INTEGER | NULLABLE | 依資產分群 |
| RookieAddBuffer | INTEGER | NULLABLE | 新手玩家灌入Buffer的分數 |
| TotalWinUsedForOrb | INTEGER | NULLABLE | 用於掉落寶珠的贏分 |
| BetToGem | INTEGER | NULLABLE | 用於寶石魚的押注 |
| GemWin | INTEGER | NULLABLE | 贏得的寶石數 |
| BetToGemTimes | INTEGER | NULLABLE | 用於寶石魚的押注次數 |
| GemWinTimes | INTEGER | NULLABLE | 捕獲寶石魚次數 |
| BetToItem | INTEGER | NULLABLE | 用於道具魚的押注 |
| BetToItemTimes | INTEGER | NULLABLE | 用於道具魚的押注次數 |
| ItemWin | INTEGER | NULLABLE | 贏得道具估算的金幣價值 |
| ItemWinTimes | INTEGER | NULLABLE | 捕獲道具魚次數 |
| CancelBet | INTEGER | NULLABLE | 取消的押注 |
| CancelBetTimes | INTEGER | NULLABLE | 取消的押注次數 |
| EnergySkillWin | INTEGER | NULLABLE | 特殊技能的贏分 |
| EnergySkillTimes | INTEGER | NULLABLE | 特殊技能的使用次數 |
| ExtraBetTimes | INTEGER | NULLABLE | extra bet的押注次數 |
| TotalExtraBet | INTEGER | NULLABLE | extra bet的押注總額 |
| ExtraBetBufferTimes | INTEGER | NULLABLE | extra bet的進入buffer的次數 |
| TotalExtraBetBuffer | INTEGER | NULLABLE | extra bet的進入buffer的額度 |
| ExtraBetType | INTEGER | NULLABLE | extra bet的類型 |
| EndRocketBuffer | INTEGER | NULLABLE | Sessino結束時火箭buffer值 |
| StartRocketBuffer | INTEGER | NULLABLE | Sessino開始時火箭buffer值 |
| TotalRocketWin | INTEGER | NULLABLE | 透過火箭的贏分 |
| TotalRocketWinTimes | INTEGER | NULLABLE | 火箭贏分次數 |
| Status | INTEGER | NULLABLE |  |
| StartBombBuffer | INTEGER | NULLABLE | Sessino開始時炸魚buffer值 |
| EndBombBuffer | INTEGER | NULLABLE | Sessino結束時炸魚buffer值 |
| HitType | STRING | NULLABLE |  |
| MainScript | STRING | NULLABLE | 主腳本名稱 |
| Script | STRING | NULLABLE | 腳本名稱 |
| WeaponSkin | INTEGER | NULLABLE | 砲台編號 |
| BufferCancelBet | INTEGER | NULLABLE | 因負Buffer強制NoWin的押注 |
| BufferCancelBetTimes | FLOAT | NULLABLE | 因負Buffer強制NoWin的押注次數 |
| PlayBonusBaseBet | INTEGER | NULLABLE |  |
| TotalPlayBonusBetTimes | INTEGER | NULLABLE |  |
| TotalPlayBonusBet | INTEGER | NULLABLE |  |
| TotalPlayBonusWin | INTEGER | NULLABLE |  |
| TotalCollectTokenBet | INTEGER | NULLABLE |  |
| TotalCollectTokenBetTimes | INTEGER | NULLABLE |  |
| TotalCollectTokenWin | INTEGER | NULLABLE |  |

**Sample (5 rows):**
```
       BQDate                         SessionID  StartEventTime  LastEventTime     UserID  BetPerShoot  QualifyForJP  BetID  TotalBetTimes   TotalBet  TotalWinTimes   TotalWin  EndBalance                                  UDID  TableTypeID  LV  VipLV SessionName  StartBalance Country  TotalJPWin  StartBuffer  EndBuffer  CutBuffer  TotalCardTimes  TotalCardWin  TotalRepayWin ClientVersion  CoinGroup  RookieAddBuffer  TotalWinUsedForOrb  BetToGem  GemWin  BetToGemTimes  GemWinTimes  BetToItem  BetToItemTimes  ItemWin  ItemWinTimes  CancelBet  CancelBetTimes  EnergySkillWin  EnergySkillTimes  ExtraBetTimes  TotalExtraBet  ExtraBetBufferTimes  TotalExtraBetBuffer  ExtraBetType  EndRocketBuffer  StartRocketBuffer  TotalRocketWin  TotalRocketWinTimes  Status  StartBombBuffer  EndBombBuffer HitType MainScript Script  WeaponSkin  BufferCancelBet  BufferCancelBetTimes  PlayBonusBaseBet  TotalPlayBonusBetTimes  TotalPlayBonusBet  TotalPlayBonusWin  TotalCollectTokenBet  TotalCollectTokenBetTimes  TotalCollectTokenWin
0  2026-05-13  0655216c737bf0321c57ebc2d09ae6f8      1778679769     1778679958  107888227         5000             0      4            952  4760000.0             56  1780000.0   3527505.0  18822680-4871-46A0-9D68-5A7762EA8D9C            8  52      1        None     6507505.0      JP         0.0            0          0          0               0             0            0.0         4.5.6          0                0                   0         0       0              0            0          0               0        0             0          0               0               0                 0              0              0                    0                    0             0           -45000                  0          145000                    1    <NA>             <NA>           <NA>    None       None   None        <NA>                0                   0.0              <NA>                    <NA>               <NA>               <NA>                  <NA>                       <NA>                  <NA>
1  2026-05-13  1b8a4ca36a7eea7013e3afdf3562f7e7      1778685578     1778685746  107888643         5000             0      4           1000  5000000.0             97  4005000.0    305798.0  83211521-7A90-4CD9-9F01-B5A5BD3B4BDB            8  14      1        None     1300798.0      CN         0.0            0          0          0               0             0            0.0         4.5.6          0                0                   0         0       0              0            0          0               0        0             0          0               0               0                 0              0              0                    0                    0             0           -40000             275000          315000                    6    <NA>             <NA>           <NA>    None       None   None        <NA>                0                   0.0              <NA>                    <NA>               <NA>               <NA>                  <NA>                       <NA>                  <NA>
2  2026-05-13  1b8a4ca36a7eea7013e3afdf3562f7e7      1778685746     1778685782  107888643         5000             0      4            153   765000.0             22   460000.0       798.0  83211521-7A90-4CD9-9F01-B5A5BD3B4BDB            8  14      1        None      305798.0      CN         0.0            0          0          0               0             0            0.0         4.5.6          0                0                   0         0       0              0            0          0               0        0             0          0               0               0                 0              0              0                    0                    0             0           -40000             -40000               0                    0    <NA>             <NA>           <NA>    None       None   None        <NA>                0                   0.0              <NA>                    <NA>               <NA>               <NA>                  <NA>                       <NA>                  <NA>
3  2026-05-13  1b8a4ca36a7eea7013e3afdf3562f7e7      1778685413     1778685578  107888643         5000             0      4           1000  5000000.0            110  4985000.0   1300798.0  83211521-7A90-4CD9-9F01-B5A5BD3B4BDB            8  14      1        None     1315798.0      CN         0.0            0          0          0               0             0            0.0         4.5.6          0                0                   0         0       0              0            0          0               0        0             0          0               0               0                 0              0              0                    0                    0             0           275000                  0               0                    0    <NA>             <NA>           <NA>    None       None   None        <NA>                0                   0.0              <NA>                    <NA>               <NA>               <NA>                  <NA>                       <NA>                  <NA>
4  2026-05-13  1ee7348976c6597ecf8cdc81599bf404      1778685897     1778685917  107888666         5000             0      4             75   375000.0              9   480000.0   2078126.0  D915AC54-9E8B-47A1-AA8E-584035B0E21A            8  22      1        None     1973126.0      CN         0.0            0          0          0               0             0            0.0         4.5.6          0                0                   0         0       0              0            0          0               0        0             0          0               0               0                 0              0              0                    0                    0             0                0                  0               0                    0    <NA>             <NA>           <NA>    None       None   None        <NA>                0                   0.0              <NA>                    <NA>               <NA>               <NA>                  <NA>                       <NA>                  <NA>
```

## `rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics`
總行數約 1,342,856,290 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | NULLABLE |  |
| UserID | INTEGER | NULLABLE |  |
| Country | STRING | NULLABLE |  |
| CountryDetail | STRING | NULLABLE |  |
| VipLV | INTEGER | NULLABLE |  |
| TableTypeID | INTEGER | NULLABLE |  |
| FishID | INTEGER | NULLABLE |  |
| Status | INTEGER | NULLABLE |  |
| BetPerShoot | INTEGER | NULLABLE |  |
| SetRTP | FLOAT | NULLABLE |  |
| TotalWinTimes | INTEGER | NULLABLE |  |
| TotalWin | FLOAT | NULLABLE |  |
| TotalBet | FLOAT | NULLABLE |  |
| TotalBetTimes | FLOAT | NULLABLE |  |
| BufferAdd | INTEGER | NULLABLE |  |
| BufferSub | INTEGER | NULLABLE |  |
| GemWin | INTEGER | NULLABLE |  |
| BufferFill | INTEGER | NULLABLE |  |
| ItemWin | INTEGER | NULLABLE |  |
| BetToItem | INTEGER | NULLABLE |  |
| BetToGem | INTEGER | NULLABLE |  |
| BombBufferAdd | INTEGER | NULLABLE |  |
| BombBufferSub | INTEGER | NULLABLE |  |

**Sample (5 rows):**
```
       BQDate     UserID Country CountryDetail  VipLV  TableTypeID  FishID  Status  BetPerShoot  SetRTP  TotalWinTimes  TotalWin  TotalBet  TotalBetTimes  BufferAdd  BufferSub  GemWin  BufferFill  ItemWin  BetToItem  BetToGem  BombBufferAdd  BombBufferSub
0  2026-05-13  107888568      CN            CN      1            4   20001       0          100     0.0              0       0.0     900.0            9.0        884          0       0           0        0          0         0              0              0
1  2026-05-13  107888568      CN            CN      1            4   20001       0          200     0.0              0       0.0    2400.0           12.0       2359          0       0           0        0          0         0              0              0
2  2026-05-13  107888568      CN            CN      1            2   20001       0         1000     0.0              0       0.0  459000.0          459.0     449820          0       0           0        0          0         0              0              0
3  2026-05-13  107888572      CN            CN      1            2   20001       0         1000     0.0              0       0.0  103000.0          103.0     100940          0       0           0        0          0         0              0              0
4  2026-05-13  107888573      JP            JP      1           28   20001       0         5000     0.0              0       0.0  410000.0           82.0     401800          0       0           0        0          0         0              0              0
```

## `rd7-data-big-query.bklog.GameConsume`
總行數約 36,846,831 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | NULLABLE |  |
| ProDate | INTEGER | NULLABLE | 資料傳送日期 |
| CreateDate | INTEGER | NULLABLE | 儲值日期 |
| CreateTime | INTEGER | NULLABLE | 儲值時間 |
| UserID | INTEGER | NULLABLE | 玩家自動ID(帳號) |
| OrderID | STRING | NULLABLE | 儲值訂單編號 |
| VenderOrderID | STRING | NULLABLE | 廠商訂單編號 |
| ExchangeRate | FLOAT | NULLABLE | 台幣參考匯率 |
| SysType | INTEGER | NULLABLE | 操作系統 |
| Country | STRING | NULLABLE | 所在地區(國別) |
| Region | STRING | NULLABLE | 所在地區(省市) |
| Channel | INTEGER | NULLABLE | 上架平台/渠道 |
| Distributor | INTEGER | NULLABLE | 儲值管道商 |
| PublishVer | STRING | NULLABLE | 遊戲版本 |
| DEV | STRING | NULLABLE | 機型 |
| SysVer | STRING | NULLABLE | 操作系統版本 |
| Resolution | STRING | NULLABLE | 解析度/分辨率 |
| Network | INTEGER | NULLABLE | 聯網方式 |
| ChargePoint | INTEGER | NULLABLE | 計費點代碼 |
| LV | INTEGER | NULLABLE | 目前等級 |
| VipLV | INTEGER | NULLABLE | 目前VIP等級 |
| SaleType | INTEGER | NULLABLE | 優惠活動類型 |
| SaleCode | STRING | NULLABLE | 優惠活動代碼 |
| BuyNumber | FLOAT | NULLABLE | 儲值金額(統計幣別) |
| BuyNumberActual | FLOAT | NULLABLE | 原始交易金額 |
| CurrencyName | STRING | NULLABLE | 原始交易幣別 |
| UserMemo | STRING | NULLABLE | 交易備註 |
| CoinAwarded | FLOAT | NULLABLE | 获得金币 |
| VIPPointAwarded | INTEGER | NULLABLE | 获得VP点数 |
| UDID | STRING | NULLABLE | 設備識別ID |
| PackageType | INTEGER | NULLABLE | 優惠包類型 |
| SaleName | STRING | NULLABLE | 優惠活動名稱 |
| Nickname | STRING | NULLABLE | 暱稱 |
| CreateTimeTs | INTEGER | NULLABLE | 儲值時間 10位數 |
| AccountCreateTime | INTEGER | NULLABLE | 帳號建立時間 |
| ResultCode | INTEGER | NULLABLE | 交易結果代碼 |
| LuckyRate | INTEGER | NULLABLE | 轉輪包優惠倍數 |
| InstallSource | STRING | NULLABLE | 第三方媒體首次安裝來源 |
| SceneState | INTEGER | NULLABLE | 場景 |
| LastSaleType | INTEGER | NULLABLE | 轉輪包前一包的 SaleType |
| LastSaleCode | STRING | NULLABLE | 轉輪包前一包的 SaleCode |
| SourceType | INTEGER | NULLABLE | 曝光來源 |
| ExcludeUserStatistics | INTEGER | NULLABLE | 排除Tag計算 |
| DuplicateBuy | INTEGER | NULLABLE | 是否為重複購買 |
| SaleFeature | INTEGER | NULLABLE | 銷售追蹤特徵 |
| BuyNumberNT | FLOAT | NULLABLE | 訂單儲值金額(新台幣幣值) |
| CenterPayType | INTEGER | NULLABLE | 訂單儲值中心付費渠道(儲值中心) |
| CenterTransID | STRING | NULLABLE | 訂單儲值中心訂單編號 |
| CurrChannel | INTEGER | NULLABLE |  |
| IsBlueDiamond | INTEGER | NULLABLE | 藍鑽禮包 |

**Sample (5 rows):**
```
       BQDate   ProDate  CreateDate        CreateTime     UserID     OrderID             VenderOrderID  ExchangeRate  SysType Country     Region  Channel  Distributor PublishVer            DEV                SysVer Resolution  Network  ChargePoint   LV  VipLV  SaleType       SaleCode  BuyNumber  BuyNumberActual CurrencyName   UserMemo  CoinAwarded  VIPPointAwarded                                  UDID  PackageType                       SaleName        Nickname  CreateTimeTs  AccountCreateTime  ResultCode  LuckyRate InstallSource  SceneState  LastSaleType LastSaleCode  SourceType  ExcludeUserStatistics  DuplicateBuy  SaleFeature  BuyNumberNT  CenterPayType CenterTransID  CurrChannel  IsBlueDiamond
0  2026-05-13  20260513    20260513  1778687431136705  107888691  P788898924           530002885198010      1.000000        2      JP  Musashino        1            2      4.5.6     iPhone17 1            iOS 26.4.2  1206x2622        0            1   19      1         2  F1758548511-0       0.99           140.00          JPY       None    1100000.0              550  16780150-04A6-48EE-86FE-3B857E9432E9            1  CRM_202509_≤25等_0.99_110萬_第1天       107888691    1778687431         1778686246           0          0     amoad_int           0             0         None           1                      0             0          462     29.63268              0          None            1              0
1  2026-05-13  20260513    20260513  1778602034302572   14445660  P788879605  GPA.3331-0882-1292-84486      1.000000        1      GB     London        2            1      4.5.6  HONOR DNP-NX9  Android OS 16 / API-  2800x1280        0            1  344      3        53     BP00100099       0.99             0.89          GBP  GP:v7.0.0          0.0                4                               Unknown            1            活動任務BattlePass_0.99  Catalin Colgiu    1778602034         1452947220           0          0       Unknown       10004             0         None           0                      1             0            0     29.63268              0          None            2              0
2  2026-05-13  20260513    20260513  1778603976272627   14445660  P788880312  GPA.3301-9226-9631-10564      1.000000        1      GB     London        2            1      4.5.6  HONOR DNP-NX9  Android OS 16 / API-  2800x1280        0            1  344      3        53     BP00100099       0.99             0.89          GBP  GP:v7.0.0          0.0                4                               Unknown            1            活動任務BattlePass_0.99  Catalin Colgiu    1778603976         1452947220           0          0       Unknown         524             0         None           0                      1             0            0     29.63268              0          None            2              0
3  2026-05-13  20260513    20260513  1778685542843952   10897320  P788898404           720002531134811      0.747107        2      SG  Singapore        2            2      4.5.6       iPad7 12           iPadOS 15.5  2160x1620        0            1  535      3        53     BP00100099       0.99             0.98          SGD       None          0.0                4  293BCF8F-B870-48AE-9DC0-59F6967577FB            1            活動任務BattlePass_0.99      Kimmy Chua    1778685542         1443286194           0          0  Facebook Ads       10004             0         None           0                      1             0            0     29.63268              0          None            1              0
4  2026-05-13  20260513    20260513  1778685385965352   10897320  P788898371           720002531129955      0.747107        2      SG  Singapore        2            2      4.5.6       iPad7 12           iPadOS 15.5  2160x1620        0            1  535      3        53     BP00100099       0.99             0.98          SGD       None          0.0                4  293BCF8F-B870-48AE-9DC0-59F6967577FB            1            活動任務BattlePass_0.99      Kimmy Chua    1778685385         1443286194           0          0  Facebook Ads       10004             0         None           0                      1             0            0     29.63268              0          None            1              0
```

## `rd7-data-big-query.bklog.RankSettlementLog`
總行數約 4,184,175 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | NULLABLE |  |
| EventID | STRING | NULLABLE | 排行榜ID |
| StartTime | INTEGER | NULLABLE | 排行榜開始時間 |
| EndTime | INTEGER | NULLABLE | 排行榜結束時間 |
| LastUpdateTime | INTEGER | NULLABLE | 事件結算時間 |
| UserID | INTEGER | NULLABLE | 玩家代號 |
| VipLV | INTEGER | NULLABLE | VIP等級 |
| Country | STRING | NULLABLE | 國家 |
| Type | STRING | NULLABLE | 排行榜類型 |
| CollectionItemType | INTEGER | NULLABLE |  |
| Score | FLOAT | NULLABLE | 積分 |
| Rank | INTEGER | NULLABLE | 排名 |
| RewardList | STRING | NULLABLE |  |
| IsGuildRank | INTEGER | NULLABLE | 是否是公會競賽 |

**Sample (5 rows):**
```
       BQDate       EventID   StartTime     EndTime  LastUpdateTime     UserID  VipLV Country            Type  CollectionItemType     Score  Rank             RewardList  IsGuildRank
0  2026-05-13  AR1777344332  1778558400  1778587199      1778628612  107886047      1      JP  M_TopNTotalWin                  -1  806000.0    18   coin_50000;I400140_1            0
1  2026-05-13  AR1777344332  1778558400  1778587199      1778628612  107847721      1      JP  M_TopNTotalWin                  -1  740000.0    23   coin_50000;I400140_1            0
2  2026-05-13  AR1777344332  1778558400  1778587199      1778628612  107773366      1      JP  M_TopNTotalWin                  -1  796000.0    19   coin_50000;I400140_1            0
3  2026-05-13  AR1777344332  1778558400  1778587199      1778628612  106106791      1      JP  M_TopNTotalWin                  -1  981800.0    11  coin_100000;I400140_2            0
4  2026-05-13  AR1777344332  1778558400  1778587199      1778628612  105214058      1      JP  M_TopNTotalWin                  -1  770000.0    21   coin_50000;I400140_1            0
```

## `rd7-data-big-query.bklog.DimActivityRankLog`
總行數約 11,450 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | NULLABLE |  |
| EventID | STRING | NULLABLE |  |
| TypeKey | STRING | NULLABLE |  |
| VipLV | STRING | NULLABLE |  |
| UserID | STRING | NULLABLE |  |
| UserIDOperation | STRING | NULLABLE |  |
| MainTab | STRING | NULLABLE |  |
| SecondTab | STRING | NULLABLE |  |
| GID | STRING | NULLABLE |  |
| RankContent | STRING | NULLABLE |  |
| IsGuild | INTEGER | NULLABLE |  |
| Bet | INTEGER | NULLABLE |  |
| GameType | STRING | NULLABLE |  |
| Country | STRING | NULLABLE |  |
| CountryOperation | STRING | NULLABLE |  |
| StartEventTime | INTEGER | NULLABLE |  |
| LastEventTime | INTEGER | NULLABLE |  |
| SwitchType | INTEGER | NULLABLE |  |
| EventTime | INTEGER | NULLABLE |  |
| ScoreLimit | INTEGER | NULLABLE |  |

**Sample (5 rows):**
```
       BQDate       EventID                 TypeKey      VipLV UserID UserIDOperation MainTab   SecondTab       GID                              RankContent  IsGuild    Bet                          GameType Country CountryOperation  StartEventTime  LastEventTime  SwitchType   EventTime  ScoreLimit
0  2026-05-13  AR1778644661  festival_special_cn_03  2,3,4,5,6   None            None    SLOT  老虎機富豪館贏分挑戰  high_495  在富豪館 - 福星高照3-超級888獲得贏分累積積分(進入排行榜門檻： ...        0  50000  S_TotalWonCoins_ExcludeFreeCards      CN              and      1778688000     1779119999           1  1778644661     3138500
```

## `rd7-data-big-query.bklog.SessionItemLog`
總行數約 8,650,573,360 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| StartEventTime | INTEGER | NULLABLE | 該session第一次事件發生時間 |
| LastEventTime | INTEGER | NULLABLE | 該session最後一次事件發生時間 |
| ItemReason | INTEGER | NULLABLE | 事件代號 |
| UserID | INTEGER | NULLABLE | 玩家代號 |
| ItemType | INTEGER | NULLABLE | 道具類型 |
| TotalEventTimes | INTEGER | NULLABLE | 總Event次數 |
| TotalItemAwarded | INTEGER | NULLABLE | 總獲得道具量 |
| EndBalance | INTEGER | NULLABLE | session結束時的玩家的道具剩餘數量 |
| UDID | STRING | NULLABLE | 設備識別ID |
| SessionID | STRING | NULLABLE | SessionID |

**Sample (5 rows):**
```
       BQDate  StartEventTime  LastEventTime  ItemReason     UserID  ItemType  TotalEventTimes  TotalItemAwarded  EndBalance                                  UDID                         SessionID
0  2026-05-13      1778604227     1778604227           1  107883434     30003                1                50          61  0B76D08F-3BE0-453F-ABD9-F4179382EE73  0adb1241b2af46ab5f118b2679dd4755
1  2026-05-13      1778604227     1778604227           1  107883434    110365                1                 3           3  0B76D08F-3BE0-453F-ABD9-F4179382EE73  0adb1241b2af46ab5f118b2679dd4755
2  2026-05-13      1778604227     1778604227           1  107883434     30005                1                10          10  0B76D08F-3BE0-453F-ABD9-F4179382EE73  0adb1241b2af46ab5f118b2679dd4755
3  2026-05-13      1778604227     1778604227           1  107883434    110261                1                 3           3  0B76D08F-3BE0-453F-ABD9-F4179382EE73  0adb1241b2af46ab5f118b2679dd4755
4  2026-05-13      1778604227     1778604227           1  107883434    110053                1                 3           3  0B76D08F-3BE0-453F-ABD9-F4179382EE73  0adb1241b2af46ab5f118b2679dd4755
```

## `rd7-data-big-query.kuochinfu.watchlist`
總行數約 1,214 | 分區: None

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| UserID | INTEGER | NULLABLE |  |
| Note | STRING | NULLABLE |  |
| GroupID | INTEGER | NULLABLE |  |
| Country | STRING | NULLABLE |  |

## `rd7-data-big-query.bklog.ActivityMissionPopUpStateLog`
總行數約 536,615,026 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED | 日期 |
| UserID | INTEGER | NULLABLE | 玩家ID |
| EventTime | INTEGER | NULLABLE | 事件發生時間 |
| VipLV | INTEGER | NULLABLE | VIP等級 |
| Country | STRING | NULLABLE | 國家 |
| EventName | STRING | NULLABLE | 活動名稱 |
| BatchID | STRING | NULLABLE | 識別用ID |
| MissionBox | STRING | NULLABLE | 任務收盒 |
| LockType | INTEGER | NULLABLE | 上鎖類別 |
| LockReason | STRING | NULLABLE | 上鎖原因 |
| ProgressState | STRING | NULLABLE | 進度條狀態 |

**Sample (5 rows):**
```
       BQDate     UserID   EventTime  VipLV Country                              EventName            BatchID           MissionBox  LockType LockReason ProgressState
0  2026-05-13  107887407  1778637148      1      KH  CG_LV1_20260501_1000_v123456_exc_cn_G  2025-05-01#f29720  CG_monthpass_domino         0          0          0_30
1  2026-05-13  107888603  1778687773      1      US  CG_LV1_20260501_1000_v123456_exc_cn_G  2025-05-01#f29720  CG_monthpass_domino         0          0          0_30
2  2026-05-13  107888603  1778687772      1      US  CG_LV2_20260501_1000_v123456_exc_cn_G  2025-05-01#f29720  CG_monthpass_domino         0          0          0_30
3  2026-05-13  107887688  1778651137      1      JP  DN_LV1_20260501_1000_v123456_exc_cn_G  2025-05-01#f29714    DN_monthpass_dino         0          0          1_30
4  2026-05-13  107887841  1778651863      1      ID  DN_LV1_20260501_1000_v123456_exc_cn_G  2025-05-01#f29714    DN_monthpass_dino         0          0          0_30
```

## `rd7-data-big-query.DailyDimData.DailyDimItemValue`
總行數約 30,304,278 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| ItemName | STRING | NULLABLE |  |
| ItemTypeName | STRING | NULLABLE |  |
| ItemLevel | STRING | NULLABLE |  |
| ItemTypeID | INTEGER | NULLABLE |  |
| VipLevel | INTEGER | NULLABLE |  |
| Value | INTEGER | NULLABLE |  |

**Sample (5 rows, no date filter):**
```
       BQDate  ItemName ItemTypeName ItemLevel  ItemTypeID  VipLevel  Value
0  2026-01-29  蛋黃酥_0916     中秋五行收集道具         -       90381         3      0
1  2026-01-29  蛋黃酥_0916     中秋五行收集道具         -       90381         1      0
2  2026-01-29  蛋黃酥_0916     中秋五行收集道具         -       90381         5      0
3  2026-01-29  蛋黃酥_0916     中秋五行收集道具         -       90381         2      0
4  2026-01-29  蛋黃酥_0916     中秋五行收集道具         -       90381         4      0
```

## `rd7-data-big-query.bklog.ExchangeActivityExchangeLog`
總行數約 21,726,705 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| EventTime | INTEGER | NULLABLE | 事件發生時間 |
| UserID | INTEGER | NULLABLE | 玩家代號 |
| LV | INTEGER | NULLABLE | 等級 |
| VipLV | INTEGER | NULLABLE | 玩家VIP等級 |
| Country | STRING | NULLABLE | 國家 |
| NickName | STRING | NULLABLE | 暱稱 |
| EventID | STRING | NULLABLE | 活動代號 |
| ExchangeID | STRING | NULLABLE | 兌換規則代號 |
| LeftExchangeTimes | INTEGER | NULLABLE | 剩餘兌換數量 |
| Times | INTEGER | NULLABLE | 兌換次數 |

**Sample (5 rows):**
```
       BQDate   EventTime     UserID   LV  VipLV Country   NickName       EventID       ExchangeID  LeftExchangeTimes  Times
0  2026-05-13  1778613102  107873646  188      2      JP  107873646  EA1777464982  EA1777464982019                 -1      1
1  2026-05-13  1778613106  107873646  188      2      JP  107873646  EA1777464982  EA1777464982019                 -1      1
2  2026-05-13  1778613043   60288252  297      2      AU   60288252  EA1777464982  EA1777464982019                 -1      5
3  2026-05-13  1778655491  107613000  347      2      AU  107613000  EA1777464982  EA1777464982018                 -1      1
4  2026-05-13  1778675377   24562917  411      3      AU   samlycan  EA1777464982  EA1777464982019                 -1      6
```

## `rd7-data-big-query.bklog.ExchangeActivityDetailLog`
總行數約 57,981,395 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| EventTime | INTEGER | NULLABLE | 事件發生時間 |
| UserID | INTEGER | NULLABLE | 玩家代號 |
| EventID | STRING | NULLABLE |  |
| ExchangeID | STRING | NULLABLE |  |
| RewardType | INTEGER | NULLABLE | 獎勵類型 |
| ItemType | INTEGER | NULLABLE | 道具ID |
| Value | INTEGER | NULLABLE | (需求/獎勵)數量 |
| ExchangeType | INTEGER | NULLABLE | Type |
| EndBalance | INTEGER | NULLABLE | 剩餘數量 |
| Times | INTEGER | NULLABLE | 兌換次數 |

**Sample (5 rows):**
```
       BQDate   EventTime     UserID       EventID       ExchangeID  RewardType  ItemType  Value  ExchangeType  EndBalance  Times
0  2026-05-13  1778613102  107873646  EA1777464982  EA1777464982019           4     92314     50             0          70      1
1  2026-05-13  1778613106  107873646  EA1777464982  EA1777464982019           4     92314     50             0          20      1
2  2026-05-13  1778613102  107873646  EA1777464982  EA1777464982019           4    150006    160             1         210      1
3  2026-05-13  1778613106  107873646  EA1777464982  EA1777464982019           4    150006    160             1         370      1
4  2026-05-13  1778622604   94938770  EA1777464982   EA177746498204           4     91342      1             1           1      1
```

## `rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog`
總行數約 10,461,333 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | REQUIRED |  |
| UserID | INTEGER | NULLABLE |  |
| GroupClusterID | STRING | NULLABLE |  |
| GroupRoleCount | INTEGER | NULLABLE |  |
| DeviceClusterID | STRING | NULLABLE |  |
| DeviceRoleCount | INTEGER | NULLABLE |  |
| IP | STRING | NULLABLE |  |
| RiskTag | STRING | NULLABLE |  |
| Category | STRING | NULLABLE |  |
| RiskLevel | STRING | NULLABLE |  |

**Sample (5 rows, no date filter):**
```
       BQDate     UserID                           GroupClusterID  GroupRoleCount     DeviceClusterID  DeviceRoleCount              IP                RiskTag Category RiskLevel
0  2025-05-03  106585737                        A2025050321295736              36   A2025050321295736               36  42.119.148.217                   高频改机   资源聚集团伙       高风险
1  2025-07-30  106957424  C20250730211296107,B2025073017122677...               6  C20250730211296107                6   182.232.105.4  多开(Client),多开(Server)   资源聚集团伙       低风险
2  2025-06-23  106824520                        A2025062321670839              69   A2025062321670839               69    42.113.60.77                   高频改机   资源聚集团伙       高风险
3  2025-12-02  107421874    C20251202221577000,B20251202221546743              11  C20251202221577000               11   65.181.16.192  多开(Server),多开(Client)   资源聚集团伙       中风险
4  2025-01-26  106248316      A2025012607253117,A2025012611256767              17   A2025012611256767               17   49.150.52.222                   高频改机   资源聚集团伙       中风险
```

## `rd7-data-big-query.preprocessed_bklog.UserOperationGroup`
總行數約 54,383,109 | 分區: BQDate

| 欄位 | 類型 | 模式 | 說明 |
|------|------|------|------|
| BQDate | DATE | NULLABLE |  |
| DateType | STRING | NULLABLE |  |
| UserID | INTEGER | NULLABLE |  |
| Country | STRING | NULLABLE |  |
| UserType | STRING | NULLABLE |  |
| UserTag | STRING | NULLABLE |  |
| Contribution | FLOAT | NULLABLE |  |
| NewUserTag | STRING | NULLABLE |  |
| NewContribution | FLOAT | NULLABLE |  |

**Sample (5 rows, no date filter):**
```
       BQDate DateType     UserID Country UserType UserTag  Contribution NewUserTag  NewContribution
0  2023-07-01  2023-07  102979097      CN     本月新進      無客           0.0         無客              0.0
1  2023-07-01  2023-07  102981415      CN     本月新進      無客           0.0         無客              0.0
2  2023-07-01  2023-07  102945265      CN     本月新進      無客           0.0         無客              0.0
3  2023-07-01  2023-07  102838931      CN     本月新進      無客           0.0         無客              0.0
4  2023-07-01  2023-07  102728005      CN     本月新進      無客           0.0         無客              0.0
```