---
inclusion: always
---

# kiro-cli 與 MCP 通訊規範

## stdin/stdout 規則

### 輸入（發送訊息給 kiro-cli）
- kiro-cli chat 模式是 **line-based**（一行一個輸入）
- 多行文字必須 flatten 成單行再送入
- 換行符用 ` ↵ ` 替代
- 檔案路徑和說明用 ` | ` 分隔

### 輸出（偵測回應完成）
- 回應完成標記：`▸ Time:` 或 `Time:`
- 長任務可能需要 3-10 分鐘
- timeout 預設 15 分鐘

## MCP Tool 使用規則

### reply() 工具
- 每次回覆用戶都必須使用 `reply()` 工具
- 回覆內容必須是繁體中文
- 單次回覆不超過 300 字

### 檔案路徑
- 收到的檔案路徑是絕對路徑，可直接使用
- 發送檔案時也使用絕對路徑

## 模型規範

| 簡稱 | 完整名稱 | 用途 |
|------|---------|------|
| opus | claude-opus-4.6 | 預設，最強 |
| sonnet | claude-sonnet-4 | 快速平衡 |
| haiku | claude-haiku-4.5 | 最快，輕量 |

- 預設使用 claude-opus-4.6
- 模型名稱必須完全匹配（不可省略版本號）
