---
inclusion: always
---

# 新使用者引導規則

## 觸發條件

如果根目錄的 `.env` 檔案**不存在**，必須：
1. 立即告知使用者需要完成初始設定
2. 讀取根目錄的 `start.md` 檔案
3. 按照 `start.md` 的步驟逐一引導使用者完成設定

## 判斷方式

在回答任何問題之前，先確認 `.env` 是否存在：
- 存在 → 正常回答
- 不存在 → 引導設定流程（參考 `start.md`）

## 引導內容摘要

1. 安裝環境（Python >= 3.11、Go >= 1.22、kiro-cli）
2. 建立 Telegram Bot（@BotFather）
3. 建立 Telegram Group（開啟 Topics、Bot 設為管理員）
4. 複製 `.env.example` → `.env`，填入 Bot Token
5. 執行 `python scripts/get_ids.py` 取得 group_id、topic_id、user_id
6. 修改 `team.yaml` 填入正確的 ID
7. 啟動 `python -m kiro_multi_agent team start`
8. 在 Telegram 測試 `/help`

完整步驟見 `start.md`。
