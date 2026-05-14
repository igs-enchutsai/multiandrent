---
inclusion: always
---

# Boss 知識庫

## 資料來源

Boss 規格資料位於：`boss-data.csv`（62 筆，含 BOSS、節慶BOSS、特殊魚）

## 欄位說明

| 欄位 | 說明 |
|------|------|
| 魚種 | Boss 名稱 |
| FishID | 魚種 ID（對應 BQ 的 FishID） |
| 類型 | BOSS / 節慶BOSS / 特殊魚 |
| 廳館 | 所在廳館（可能多個） |
| 玩法說明 | 核心玩法機制（逗號分隔） |
| 上線時的機率設計 | 機率相關設計 |
| 柏青化 | 柏青化元素（激熱/預兆/復活/升級/Push/炫彩） |
| Client製程 | 3D / SPINE / 序列圖 |
| Client資料夾名稱 | 程式內部名稱 |
| 上線日期 | 上線時間 |

## 玩法機制分類

從資料中提取的玩法機制：
- **贏分累積**：累積贏分達標觸發獎勵
- **無限抽取**：可無限次抽取獎勵
- **全永生 / 半永生**：Boss 不會死亡 / 有條件不死
- **乘倍 / 累積乘倍**：倍率機制
- **顯性倍數 / 顯性次數**：玩家可見的倍數/次數
- **小報獎**：小額獎勵回饋
- **過關制**：分階段挑戰
- **復活**：Boss 可復活
- **升級**：Boss 可升級變強
- **玩家互動**：需要玩家操作
- **加次數**：增加攻擊次數
- **進度累積**：長期進度條
- **炸場**：全場爆發效果
- **輪盤**：轉盤機制

## 柏青化元素分類

- **激熱**：高期待演出
- **預兆**：出現前的暗示
- **復活**：死後復活的驚喜
- **升級**：逐步變強的成就感
- **Push**：推動感/壓迫感
- **炫彩**：視覺華麗效果

## 數據查詢方式

需要 Boss 遊玩數據時，透過 leader 請 data-hancock 查詢：
- `rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics`：每日每玩家每魚種的押量數據
- `rd7-data-big-query.bklog.TigerSharkFishStatisticLog`：更細顆粒度的魚機遊玩數據
- `rd7-data-big-query.bklog.SessionTigerSharkBetWinLog`：廳館層級的遊玩數據

或透過 cha-cha-gin-agent 用自然語言快速查詢。
