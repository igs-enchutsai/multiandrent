"""Build the final query reference from Query Warehouse with confirmed versions."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from scripts.build_schema_knowledge import read_google_sheet

sheet_id = os.getenv("QUERY_WAREHOUSE_SHEET_ID")
data = read_google_sheet(sheet_id)
rows = data[0]["data"]
headers = rows[0]

# Final version selections for multi-query rows
# Format: row_index -> column_index (3=Query, 4=note, 5=Column1, 6=Column2)
FINAL_SELECTIONS = {
    17: 3,   # Query - 完整主體
    30: 3,   # Query - note 自標第一版
    31: 5,   # Column 1 - 加入 MissionFeatureCHT
    33: 4,   # note - 改良為可擷取模式
    34: 4,   # note - 可擷取
    35: 5,   # Column 1 - 整合訂單角度+包含未購買任務
    36: 5,   # Column 1 - 用戶選擇
    40: 4,   # note - Query 只是標題
    48: 6,   # Column 2 - 5/10 更新最新版
    50: 4,   # note - 更完整有 JOIN
}

output_dir = Path("agents/data-hancock/.kiro/steering")
lines = [
    "---",
    "inclusion: always",
    "---",
    "",
    "# Query Warehouse — 最終版本參考",
    "",
    "以下為經確認的最終版本 SQL 範例，供撰寫新 query 時參考。",
    "",
]

for j in range(1, len(rows)):
    row = rows[j]
    if len(row) < 4:
        continue

    label = row[0] if len(row) > 0 else ""
    task = row[1] if len(row) > 1 else ""
    desc = row[2] if len(row) > 2 else ""

    # Determine which column to use
    if j in FINAL_SELECTIONS:
        col_idx = FINAL_SELECTIONS[j]
    else:
        col_idx = 3  # Default to Query column

    if col_idx >= len(row) or not row[col_idx].strip():
        # Fallback: find first non-empty query column
        for try_idx in [3, 4, 5, 6]:
            if try_idx < len(row) and row[try_idx].strip():
                col_idx = try_idx
                break
        else:
            continue

    query_content = row[col_idx].strip()
    if not query_content or len(query_content) < 20:
        continue

    lines.append(f"## [{label}] {task}")
    if desc:
        lines.append(f"**描述：** {desc}")
    lines.append("")
    lines.append("```sql")
    lines.append(query_content)
    lines.append("```")
    lines.append("")

content = "\n".join(lines)
output_path = output_dir / "query-warehouse-final.md"
output_path.write_text(content, encoding="utf-8")

# Remove the old verbose version
old_path = output_dir / "query-warehouse.md"
if old_path.exists():
    old_path.unlink()

print(f"Done! Saved {len(lines)} lines to {output_path}")
print(f"Removed old query-warehouse.md")
