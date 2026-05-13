---
inclusion: always
---

# Coding Rules

## Naming
| Element | Style | Example |
|---------|-------|---------|
| Module | snake_case.py | team_mcp.py |
| Class | PascalCase | TeamManager |
| Function | snake_case | start_instance() |
| Constant | UPPER_SNAKE | READY_PATTERN |
| Enum member | UPPER_SNAKE | InstanceStatus.RUNNING |

## Style
- Every .py starts with docstring + from __future__ import annotations
- All public functions must have type annotations
- Use dataclass for config/state, not dict
- asyncio for all I/O operations
- Logging: log = logging.getLogger(__name__), use %s format

## Safety
- YAML: always yaml.safe_load() (never yaml.load())
- Tokens from env vars, never hardcoded
- .env must be in .gitignore

## 環境變數規範（必須遵守）

### 規則
1. **所有 API key、token、密碼、外部服務 URL 必須放在根目錄 `.env`**
2. 程式碼中不可出現任何 hardcoded 的 secret 或外部服務位址
3. 讀取方式：透過 `os.Getenv()` (Go) 或 `os.getenv()` (Python)
4. 未設定時應回傳明確錯誤訊息，不可用 hardcoded fallback
5. Agent 目錄下不可有獨立的 `.env` 檔案，統一由根目錄管理
6. MCP server 的 env 區塊使用 `${VAR_NAME}` 語法引用環境變數

### .env 檔案位置
- 唯一位置：專案根目錄 `.env`
- 已在 `.gitignore` 中排除

### 範例
```go
// 正確
apiKey := os.Getenv("HOYEAH_API_KEY")
if apiKey == "" {
    return "錯誤：未設定 HOYEAH_API_KEY"
}

// 錯誤
apiKey := "71ae11c594ad..."
```
