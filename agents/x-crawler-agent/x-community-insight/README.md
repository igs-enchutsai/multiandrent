# X Community Insight

X/Twitter 競品社群爬蟲與玩家反饋分析工具。

使用 Playwright 本地瀏覽器蒐集公開可見資料，並透過規則式分類產出玩家反饋分析報告。

## 安裝

```bash
cd x-community-insight
npm install
npx playwright install chromium
```

## 初始化資料庫

```bash
npm run db:init
```

## 使用方式

### 1. 登入 X（可選，部分內容需要登入才可見）

```bash
npm run cli -- login
```

瀏覽器會開啟 X 登入頁面，手動登入後按 `Ctrl+C` 關閉。登入狀態會保存在本地。

### 2. 新增競品

```bash
npm run cli -- competitor:add --name "Game A" --url "https://x.com/game_a"
```

### 3. 列出競品

```bash
npm run cli -- competitor:list
```

### 4. 爬取競品帳號頁面

```bash
npm run cli -- crawl:account --competitor "Game A" --max-posts 100 --days 30
```

### 5. 爬取指定貼文及留言

```bash
npm run cli -- crawl:post --url "https://x.com/game_a/status/123456789" --passes 3 --max-replies 500
```

### 6. 分析反饋

```bash
npm run cli -- analyze --competitor "Game A" --days 30
```

### 7. 匯出報告

```bash
# Markdown 格式
npm run cli -- export --competitor "Game A" --format markdown

# JSON 格式
npm run cli -- export --competitor "Game A" --format json

# CSV 格式
npm run cli -- export --competitor "Game A" --format csv
```

報告會輸出到 `data/exports/` 目錄。

## 專案結構

```
x-community-insight/
├── package.json
├── tsconfig.json
├── .env.example
├── apps/
│   └── worker/
│       └── src/
│           ├── cli.ts              # CLI 入口
│           ├── crawler/
│           │   ├── browser.ts      # Playwright 瀏覽器管理
│           │   ├── post-crawler.ts # 貼文爬取
│           │   ├── account-crawler.ts # 帳號頁爬取
│           │   └── media-downloader.ts # 圖片下載
│           ├── analyzer/
│           │   └── feedback-analyzer.ts # 反饋分類分析
│           ├── database/
│           │   ├── migrate.ts      # Schema 與初始化
│           │   └── repository.ts   # 資料存取層
│           ├── exporters/
│           │   └── report-exporter.ts # 報告匯出
│           └── utils/
│               └── helpers.ts      # 工具函數
├── config/
│   └── feedback-rules.yaml         # 反饋分類規則（可自訂）
└── data/
    ├── database.sqlite             # SQLite 資料庫
    ├── media/                      # 下載的圖片
    ├── exports/                    # 匯出的報告
    └── logs/                       # 爬取日誌
```

## 反饋分類規則

編輯 `config/feedback-rules.yaml` 可自訂分類關鍵字。支援中文、英文、日文。

## 注意事項

1. **僅蒐集公開可見資料** — 不使用任何繞過驗證的方式
2. **不保證 X 頁面每次載入內容一致** — 留言可能因演算法而不同
3. **不要高頻率請求** — 預設每次操作間隔 3-8 秒
4. **不要用來繞過網站限制** — 若遇到限制請停止使用
5. **若 X 頁面結構改版** — 需要更新 `post-crawler.ts` 中的 selector
6. **建議人工抽樣檢查資料品質** — 自動蒐集可能有遺漏

## 資料完整度評分

| 分數 | 說明 |
|------|------|
| 90-100 | 資料相對完整 |
| 70-89 | 資料可用但可能遺漏 |
| 50-69 | 資料不足，需要再次執行 |
| < 50 | 不建議直接做結論 |

## 技術限制

- 未使用 X API（未購買）
- 不使用代理池
- 不自動破解登入或 Captcha
- 登入狀態僅保存在本地 browser profile
