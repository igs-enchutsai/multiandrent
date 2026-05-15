---
inclusion: always
---

# 測試與驗證規範

## 修改程式碼後必須驗證

1. **語法檢查**：`python -c "import ast; ast.parse(open('file.py').read())"`
2. **import 檢查**：確認模組可正確 import
3. **API 端點測試**：修改 API 後用 curl/urllib 測試

## 常見陷阱

### FastAPI + `from __future__ import annotations`
- Pydantic BaseModel 必須定義在模組層級
- 不可定義在函數內部（會導致 422 錯誤）

### kiro-cli stdin
- 多行文字必須 flatten 成單行
- 換行符用 ` ↵ ` 替代

### 檔案路徑
- 傳給 agent 的路徑必須是絕對路徑
- 使用 `path.resolve()` 轉換

### Port 衝突
- 啟動前確認 port 未被佔用
- 停止服務時確保所有子 process 都被終止
