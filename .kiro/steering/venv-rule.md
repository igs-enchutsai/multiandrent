---
inclusion: always
---

# 虛擬環境規範（強制）

## 規則

**所有 Python 專案必須使用 `uv` 管理虛擬環境與依賴，禁止安裝套件到全局。**

## 工具：uv

- uv 是 Rust 實作的 Python 套件管理器，速度極快
- 官方文件：https://docs.astral.sh/uv/

## 本專案環境

- 位置：專案根目錄 `.venv/`（uv 預設）
- 已在 `.gitignore` 中排除

## 常用指令

```bash
# 初始化專案（建立 venv + 安裝依賴）
uv sync

# 安裝套件
uv add <package>

# 安裝開發依賴
uv add --dev <package>

# 執行 Python
uv run python -m xxx

# 執行專案 CLI
uv run kiro-multi-agent team start

# 啟動服務
uv run python -m kiro_multi_agent team start
```

## 禁止事項

- ❌ 禁止 `py -m pip install` 或 `pip install`（全局安裝）
- ❌ 禁止 `pip install --user`（user 層級安裝）
- ❌ 禁止在沒有 uv 管理的環境下執行專案程式碼
- ❌ 禁止手動建立 venv（由 uv 自動管理）

## 新專案 / 新環境初始化 SOP

```bash
# 1. 安裝 uv（如果還沒裝）
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 初始化並安裝依賴
uv sync

# 3. 確認
uv run python --version
```
