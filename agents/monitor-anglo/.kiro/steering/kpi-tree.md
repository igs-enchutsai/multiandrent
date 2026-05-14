---
inclusion: always
---

# 遊戲營運 KPI 指標樹

## 頂層指標拆解

```
營收 (Revenue)
├── 付費用戶數 (Paying Users) = DAU × 付費率
│   ├── DAU
│   │   ├── 新用戶 (New Users)
│   │   ├── 回流用戶 (Returning Users)
│   │   └── 留存用戶 (Retained Users) = 前日DAU × 次留率
│   └── 付費率 (Conversion Rate)
│       ├── BP 購買率
│       ├── 直購商品購買率
│       └── 排行榜參與率
├── ARPPU (Average Revenue Per Paying User)
│   ├── 平均訂單金額
│   └── 人均訂單次數
└── 活動營收佔比
    ├── BP 營收
    ├── 排行榜營收
    └── 其他活動營收
```

## 活躍度拆解

```
DAU
├── 新增用戶
│   ├── 自然新增
│   └── 廣告導入
├── 留存用戶 (前日活躍且今日仍活躍)
│   ├── 次日留存率
│   ├── 7日留存率
│   └── 30日留存率
└── 回流用戶 (曾流失後回來)
    ├── 自然回流
    └── 活動召回
```

## 異常判定標準（量化）

| 指標 | 輕微異常 | 中度異常 | 嚴重異常 |
|------|---------|---------|---------|
| DAU | DoD -5%~-10% | DoD -10%~-20% | DoD > -20% |
| Revenue | DoD -10%~-15% | DoD -15%~-30% | DoD > -30% |
| ARPU | WoW -5%~-10% | WoW -10%~-20% | WoW > -20% |
| 付費率 | DoD -0.5pp | DoD -1pp | DoD > -2pp |
| 次留率 | DoD -2pp | DoD -5pp | DoD > -10pp |

（DoD = Day over Day, WoW = Week over Week, pp = percentage point）

## 常見異常原因 Checklist

### DAU 下降
- [ ] 是否有活動結束？（活動結束後 DAU 自然回落）
- [ ] 是否有版本更新/維護？
- [ ] 是否為週末/假日效應？
- [ ] 是否有競品大型活動？
- [ ] 新用戶獲取是否下降？
- [ ] 留存率是否下降？

### Revenue 下降
- [ ] DAU 是否同步下降？（量的問題）
- [ ] ARPPU 是否下降？（質的問題）
- [ ] 付費率是否下降？
- [ ] 是否有高價值活動結束？
- [ ] 大客/超大客是否流失？
- [ ] 是否有異常退款？

### 活動效果不佳
- [ ] 曝光是否足夠？（ActivityMissionPopUpStateLog）
- [ ] 門檻設定是否合理？
- [ ] 獎勵是否有吸引力？
- [ ] 目標受眾是否正確？
- [ ] 是否與其他活動衝突？

## 資料需求模板

當需要 data-hancock 撈資料時，使用以下格式：

```
需求：[一句話描述]
時間範圍：[start_date] ~ [end_date]
粒度：[BQDate / BQDate + UserID / ...]
需要的欄位：[列出]
篩選條件：[Country, VIP, etc.]
對照基準：[同比/環比/特定日期]
```
