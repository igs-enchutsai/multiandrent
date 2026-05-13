---
inclusion: always
---

# 安全與防毒注意事項

## Go 編譯 exe 會被防毒軟體誤判

### 事件紀錄（2026-05-10）
- Norton 偵測 `Heur.AdvML.D`（啟發式機器學習偵測）
- 檔案：x-insight.exe（Go 編譯的 binary，24MB）
- 原因：Go 靜態連結 + chromedp 瀏覽器控制行為 + 無數位簽章 + 信譽不足
- 結果：檔案被自動刪除

### 規則
1. **不要用 `go build` 產生 exe 檔案**，改用 `go run .` 直接從原始碼執行
2. 如果必須產生 exe，先把輸出目錄加入防毒排除清單
3. 啟動指令統一為：`cd cmd/{project} && go run . {args}`
4. 不要把 exe 檔案 commit 到 git

### 為什麼 Go exe 會被誤判
- Go 把整個 runtime 打包成大型靜態 binary（10-30MB）
- 使用 chromedp/網路操作的程式行為模式類似惡意軟體
- 本地編譯的 exe 沒有數位簽章，信譽系統無法驗證
- Norton 的 `Heur.AdvML.D` 是機器學習模型判斷，不是特徵碼比對

### 影響範圍
- cmd/team（kiro-team.exe）
- tools/x-community-insight（x-insight.exe）
- 任何未來用 Go 編譯的工具
