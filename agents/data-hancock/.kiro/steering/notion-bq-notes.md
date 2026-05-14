---
inclusion: always
---

# BigQuery 資料表筆記（來自 Notion）

▶ Schema
  BattlePassBuyLog: 玩家付費解鎖任一個BP活動時觸發 1 row
  ActivityMissionReward: 點擊領取任務獎勵按鈕時觸發多 rows（玩家在該條領幾個任務就幾筆）
  ActivityMissionComplete: 玩家只要完成任務時就觸發 1 row
▶ Definition
  DimGame_ID: 所有機台的ID與名字對照，包含虎機、魚機，但是此處的 game_id 不等於其他表的TableTypeID
  DimTableTypeID: 廳館ID對應廳館中文 (TableTypeID只有魚機，GameID 含魚+虎)
▶ ActivityMissionDimLog: 定義表。上傳一個活動時就觸發多條rows
  BQDate 是標示每天在線上的活動 (EventName) 及其資訊
  PK: mission_id + VIPLV
  mission_id = EventName + suffix(門檻)
  AcitivityType: 該任務上在哪個母頁籤上
  PagePriority: 該任務在母頁籤的第幾個按鈕
  MissionName: 任務內容
  Rule: 任務內容類型，slot_totalwin, slot_singlewin…..
  TargetTimes: BP設定檔中count的欄位
  ActivityGameID: 任務內容出在哪個機台上(從appendrules 拼接)，null數較GameType多(有被判斷到GameType為哪種的，ActivityGameID不一定會被判斷到)
  GameType: 任務內容的類型
  BattlePassBuyNumber: BP 售價
  MissionFeatureCHT: missionfeature (RR,SO,IN,VT) 對應到的意思 (營收、社交、深度、活躍)
  GameCategory: BP設定檔中的BP類型 
  最細顆粒到 MissionID + VIP Level，其中VIP Level只有有開放的才會有資料。
### 其他常用表（整理版）
| 表名 | 用途 | 最細顆粒度 / PK | 備註 |
| MissionList | ActivityMissionDimLog 的中轉表（沒有 MissionID 維度） | EventName (MissionDImLog 那張同樣的EventName取BatchIDTs大的) | MissionStartDate / MissionEndDate：一檔活動始末
ActivityStartTime / ActivityEndTime：單一 MissionBookMark 始末
MissionUUID: 根據MissionLevelInfo產生的，若MissionLevelInfo一樣則MissionUUID一樣
MissionLevelInfo: 以json格式儲存資料，每個element有MissionPriority, MissionName, MissionValue, BPMissionValue, BufferRate_Free, BufferRate_Pay, Cycle, RunDay, BattlePassBuyNumber。
GameType: 原本是null改成others
ActivityGameID:  直接拿MissionDim，MissionDim null的改成others
GameID(虎機機台、魚機廳館): 從ActivityGameID 對到的GameID |
| UserInfo | 使用者自創帳以來的「最新狀態」 | user_id（unique） | 適合拿來做使用者屬性的最新值（例如 VIP 等級、累積儲值等） |
| DailyUserInfoSnapshot | 每日活躍用戶快照（只要當天有開遊戲遊玩就會記錄） | BQDate + user_id（user_id 會重複） | Google Sheet
用處：常用統計指標的中轉，減少計算量與重工
注意：早上 8 點才會有昨天資料 |
| GenToCoinGiftLog | 贈送金幣與寶石的紀錄 | （依事件而定） | 常用於追蹤贈幣、補償、活動發放等 |
| SessionActive | 活躍用戶紀錄（登入大廳即算活躍，不代表一定有遊玩） | 1 次登入 = 1 row | Google Sheet |
| UserGrossRetLog | 平台所有金幣金流數據（以 user 角度彙整） | （依 session / event 而定） | 下方已有更完整的說明區塊 |
- UserGrossRetLog: 存平台所有金幣金流的數據
- NewNESockPuppetUserLog: 風險帳戶。源於第三方服務，若玩家被檢測出有問題就會觸發1 row
- User Operation Group: 每個玩家的標籤。一個月為一個週期
- SessiontigershotbetwinLog 海王遊玩數據: 玩家在海王遊玩時的bet紀錄等等。魚機內的玩家遊玩數據。依session (一小時觸發1 row) 來記錄哪個玩家在哪個廳館玩了多少等等
- TigerSharkFishStatisticLog: 比sessiontigershotbetwinlog顆粒度再細一層。從魚的角度出發的遊玩session紀錄
- rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics : 比 TigerSharkFishStatisticLog的顆粒度再粗。顆粒度到BQDate + UserID + FishID + BetPerShoot 
- DimTableTypeID: 廳館對應中文名稱 
- DimGame_ID: 機台對應中文名稱
- TigerSharkOdd: 魚種ID對應的魚種中文名
- GameAccount: 哪些 UserID 是員工帳戶
- GameConsume: 總營收表。一筆訂單就1 row、即時更新
- GameConsumeGet: 總營收表GameConsume 顆粒度再細一層，每筆訂單的每個reward為1 row
- UserInfo: 玩家創帳國家及各種使用者屬性
- RankSettlementLog: 排行榜的結算資料。排行榜結算時會依照玩家看到的排行榜結果 insert 新的資料 (沒結算時沒資料)
- rd7-data-big-query.bklog.DimActivityRankLog: 排行榜的設定檔資料
- SessionItemLog: 玩家獲取、消耗道具的資料
- rd7-data-big-query.kuochinfu.watchlist: 我們關注的玩家(若是黑鑽，GroupID = 1)
- rd7-data-big-query.bklog.ActivityMissionPopUpStateLog: BP曝光
- Dailyuserinfosnapshot: 每天每個玩家的資料結算
- rd7-data-big-query.DailyDimData.DailyDimItemValue: 道具相關資訊
- rd7-data-big-query.bklog.ExchangeActivityExchangeLog: 五行奪寶的兌換紀錄(只有領獎)
- rd7-data-big-query.bklog.ExchangeActivityDetailLog : 五行奪寶的兌換紀錄，包含消費token跟拿回獎勵。玩家兌換一次時就會產生兩筆資料，一筆紀錄他花了多少token(Type = 0) 一筆紀錄他獲得甚麼(Type = 1)
-  rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics  : tigersharkfishstatitsic的粗版: 包含每天每個玩家打不同魚種的資料 (有切押注段 PK為: BQDate + UserID + TableTypeID + FIshID + Status + BetPerShoot)
- SlotHourlyAgg:  sessionbetwinlog 顆粒到小時的中轉表
- FishHourlyAgg:  sessiontigersharkbetwinlog 顆粒到小時的中轉表
