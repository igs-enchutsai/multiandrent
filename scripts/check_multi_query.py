"""Check which Query Warehouse rows have multiple query columns."""
from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

from scripts.build_schema_knowledge import read_google_sheet

sheet_id = os.getenv("QUERY_WAREHOUSE_SHEET_ID")
data = read_google_sheet(sheet_id)
rows = data[0]["data"]
headers = rows[0]

# Find query-related column indices
query_cols = [i for i, h in enumerate(headers) if h.lower() in ("query", "note", "column 1", "column 2")]
print(f"Headers: {headers}")
print(f"Query columns (indices): {query_cols}")
print(f"Total rows: {len(rows) - 1}")
print()

multi_rows = []
for j in range(1, len(rows)):
    row = rows[j]
    filled = sum(1 for i in query_cols if i < len(row) and row[i].strip())
    if filled > 1:
        label = row[0] if len(row) > 0 else ""
        task = row[1] if len(row) > 1 else ""
        multi_rows.append((j, label, task, filled))

print(f"Rows with multiple query/note columns filled: {len(multi_rows)}")
for j, label, task, count in multi_rows:
    print(f"  Row {j}: [{label}] {task} ({count} columns filled)")
