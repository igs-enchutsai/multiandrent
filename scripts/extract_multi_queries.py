"""Extract rows with multiple query columns for review."""
from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

from scripts.build_schema_knowledge import read_google_sheet

sheet_id = os.getenv("QUERY_WAREHOUSE_SHEET_ID")
data = read_google_sheet(sheet_id)
rows = data[0]["data"]
headers = rows[0]

# Query-related column indices: Query(3), note(4), Column 1(5), Column 2(6)
query_cols = {"Query": 3, "note": 4, "Column 1": 5, "Column 2": 6}

multi_rows = [17, 30, 31, 33, 34, 35, 36, 40, 48, 50]

for j in multi_rows:
    row = rows[j]
    label = row[0] if len(row) > 0 else ""
    task = row[1] if len(row) > 1 else ""
    desc = row[2] if len(row) > 2 else ""
    
    print(f"\n{'='*80}")
    print(f"Row {j}: [{label}] {task}")
    print(f"Description: {desc}")
    print(f"{'='*80}")
    
    for col_name, idx in query_cols.items():
        if idx < len(row) and row[idx].strip():
            content = row[idx].strip()
            # Show first 500 chars
            preview = content[:500] + ("..." if len(content) > 500 else "")
            print(f"\n--- {col_name} (col {idx}, {len(content)} chars) ---")
            print(preview)
