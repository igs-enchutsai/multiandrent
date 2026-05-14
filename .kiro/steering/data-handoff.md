---
inclusion: always
---

# Agent 間資料傳遞規範

## 目的

統一 Agent 之間傳遞資料的格式，確保接收方能正確解讀。

## 資料傳遞格式

### data-hancock → analyst-andrew（分析用資料）

傳遞完整 dataframe 描述：
```
📦 資料已準備

表名：[描述]
行數：X rows
欄位：col1 (type), col2 (type), ...
時間範圍：YYYY-MM-DD ~ YYYY-MM-DD
粒度：[BQDate + UserID / ...]

資料摘要：
- [關鍵統計]

SQL：
[完整 SQL]
```

### data-hancock → monitor-anglo（診斷用資料）

傳遞趨勢數據 + 維度拆解：
```
📦 趨勢資料

指標：[DAU / Revenue / ...]
時間範圍：最近 N 天
異常日期：YYYY-MM-DD（DoD -X%）

趨勢：
日期 | 指標值 | DoD%
...

維度拆解：
[按 VIP / 新舊 / 平台 等維度的數據]
```

### monitor-anglo → event-king（診斷結果）

```
🔍 診斷完成

根因：[一句話]
信心度：高/中/低
證據：[數據支撐]
建議：[行動建議]
```

### analyst-andrew → event-king（分析結果）

```
📊 分析完成

結論：[一句話含數字]
方法：[使用的方法]
效應：[點估計 + CI]
顯著性：[p-value]
建議：[業務建議]
```

## 規則

1. **傳遞資料時必須附上 SQL**（讓接收方可驗證）
2. **大量資料不要直接貼**（超過 20 行用摘要 + SQL）
3. **必須標明粒度和時間範圍**
4. **數值必須標明單位**（金額=台幣/美金、時間=天/小時）
