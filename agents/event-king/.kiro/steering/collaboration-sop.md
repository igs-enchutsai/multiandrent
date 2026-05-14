---
inclusion: always
---

# 多 Agent 協作流程 SOP

## 單一 Agent 任務（簡單問題）

```
用戶提問 → 判斷類型 → send_to_instance(target) → 等待回覆 → 整合回覆用戶
```

範例：「昨天 CN 營收多少？」→ 直接派給 data-hancock

## 多 Agent 協作（複合問題）

### 模式 A：串行（資料 → 分析）

```
用戶提問 → 拆解任務
  → Step 1: send_to_instance("data-hancock", "撈取 XXX 資料")
  → 等待 data-hancock 回覆
  → Step 2: send_to_instance("analyst-andrew", "用以下資料做 XXX 分析：[data-hancock 的結果]")
  → 等待 analyst-andrew 回覆
  → 整合兩者結果回覆用戶
```

範例：「這次 BP 活動的因果效應是多少？」
1. 先讓 data-hancock 撈 BP 購買者 + 對照組的前後數據
2. 再讓 analyst-andrew 用這些數據做因果推論

### 模式 B：串行（資料 → 診斷）

```
用戶提問 → 拆解任務
  → Step 1: send_to_instance("data-hancock", "撈取 XXX 指標的趨勢資料")
  → 等待回覆
  → Step 2: send_to_instance("monitor-anglo", "以下數據出現異常，請診斷：[data]")
  → 等待回覆
  → 整合回覆用戶
```

範例：「昨天 DAU 為什麼掉了？」
1. 先讓 data-hancock 撈 DAU 趨勢 + 各維度拆解
2. 再讓 monitor-anglo 用議題樹診斷根因

### 模式 C：並行（多個獨立子任務）

```
用戶提問 → 拆解為獨立子任務
  → 同時 send_to_instance("data-hancock", "任務 A")
  → 同時 send_to_instance("monitor-anglo", "任務 B")
  → 等待所有回覆
  → 整合回覆用戶
```

## 分派訊息格式

發給其他 Agent 的訊息必須包含：
1. **任務目標**：一句話說明要做什麼
2. **具體需求**：需要什麼資料/分析
3. **時間範圍**：如果涉及資料查詢
4. **輸出格式**：期望回傳什麼

範例：
```
send_to_instance("data-hancock", 
  "任務：撈取昨天 CN 各 VIP 等級的 DAU 和營收。
   時間：昨天（BQDate = current_date - 1）
   粒度：VIP 等級
   需要欄位：VipLV, DAU, Revenue, ARPU
   篩選：Country = CN")
```

## 用戶意圖分類

| 意圖類型 | 關鍵詞 | 分派 |
|---------|--------|------|
| 查數據 | 「多少」「查」「撈」「列出」 | data-hancock |
| 找原因 | 「為什麼」「原因」「下降」「異常」 | monitor-anglo（需先撈資料） |
| 評效果 | 「成效」「效果」「因果」「影響」 | analyst-andrew（需先撈資料） |
| 做預測 | 「預測」「趨勢」「未來」 | analyst-andrew |
| 做報告 | 「報告」「整理」「摘要」 | 自己整合 |
| 閒聊 | 非業務問題 | 自己回覆 |

## 回覆整合原則

1. **不要只轉發**：整合各 Agent 的回覆，用自己的話重新組織
2. **先結論後細節**：最重要的發現放最前面
3. **標註來源**：「根據分析安德魯的因果推論...」
4. **補充建議**：基於所有 Agent 的結果，給出綜合建議
