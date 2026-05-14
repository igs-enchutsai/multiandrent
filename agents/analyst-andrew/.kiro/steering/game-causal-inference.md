---
inclusion: always
---

# 遊戲營運因果推論實戰指南

## BP（Battle Pass）活動成效分析模板

### Treatment 定義
- Treatment: 購買 BP（BattlePassBuyLog 有紀錄）
- Control: 同期活躍但未購買 BP 的玩家
- Treatment Period: 活動開始日 ~ 結束日

### 常用 Outcome 指標
| 指標 | 來源表 | 計算方式 |
|------|--------|---------|
| 營收貢獻 | DailyUserInfoSnapshot | BuyNumber + (TotalCoinReceived - TotalCoinSent) / 4000000 |
| 活躍天數 | SessionActive | COUNT(DISTINCT LoginDate) |
| 遊玩押量 | SessionTigerSharkBetWinLog / SessionBetWinLog | SUM(TotalBet) |
| 任務完成率 | ActivityMissionCompleteLog | MAX(MissionPriority) + 1 |

### 推薦方法選擇

| 情境 | 推薦方法 | 原因 |
|------|---------|------|
| BP 購買 vs 未購買 | PSM + DID | 購買是自選（非隨機），需配對消除選擇偏誤 |
| 活動上線前後比較 | CausalImpact | 時間序列，有明確介入時間點 |
| 不同 VIP 等級的效應差異 | Causal Forest | 估計異質性處理效應（HTE） |
| 排行榜門檻效應 | RDD | 門檻附近的玩家近似隨機 |
| 搶救活動（針對流失玩家） | DID + PSM | 前後比較 + 配對 |

### Confounders 清單（必須控制）
- VIP 等級（付費能力）
- 活動前活躍天數（活躍度）
- 活動前營收貢獻（付費習慣）
- 帳號年齡（新舊用戶）
- 是否為風險帳戶（NewNESockPuppetUserLog）
- UserOperationGroup 標籤（大客/中客/小客）

## 排行榜成效分析模板

### Treatment 定義
- Treatment: 參與排行榜（RankSettlementLog 有結算紀錄）
- 門檻效應: 排名在獎勵門檻附近的玩家（RDD）

### 關鍵指標
| 指標 | 意義 |
|------|------|
| 押量增量 | 排行榜期間 vs 前期的 TotalBet 差異 |
| RTP | 獎勵發放 / 押量增量（排行榜的投資報酬率） |
| 參與率 | 有押量的玩家 / 目標群體 |

## 敏感性分析 Checklist

每次因果推論結果都必須回答：
1. ✅ 如果有未觀察到的 confounder，結論會改變嗎？（Rosenbaum bounds）
2. ✅ 換一個配對方法，結果一致嗎？
3. ✅ 改變時間窗口，結果穩健嗎？
4. ✅ 排除極端值後，結果一致嗎？
