"""Build data-hancock's schema knowledge from Notion, Google Sheets, and BigQuery.

Steps:
1. Read Notion BQ notes page
2. Read Query Warehouse from Google Sheets
3. Identify tables used
4. Query each table (BQDate = yesterday, LIMIT 100) to understand structure
5. Output steering files for data-hancock
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── Notion ───────────────────────────────────────────────────────

def read_notion_page(page_id: str) -> str:
    """Read all blocks from a Notion page and return as markdown-like text."""
    from notion_client import Client

    token = os.getenv("NOTION_API_TOKEN")
    if not token:
        print("ERROR: NOTION_API_TOKEN not set")
        return ""

    notion = Client(auth=token)
    blocks = []
    cursor = None

    while True:
        kwargs = {"block_id": page_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        response = notion.blocks.children.list(**kwargs)
        blocks.extend(response["results"])
        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")

    lines = []
    for block in blocks:
        block_type = block["type"]
        if block_type in ("paragraph", "bulleted_list_item", "numbered_list_item"):
            rich_text = block[block_type].get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_text)
            if block_type == "bulleted_list_item":
                text = f"- {text}"
            elif block_type == "numbered_list_item":
                text = f"1. {text}"
            lines.append(text)
        elif block_type.startswith("heading"):
            rich_text = block[block_type].get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_text)
            level = int(block_type[-1])
            lines.append(f"{'#' * level} {text}")
        elif block_type == "code":
            rich_text = block[block_type].get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_text)
            lang = block[block_type].get("language", "")
            lines.append(f"```{lang}")
            lines.append(text)
            lines.append("```")
        elif block_type == "table":
            # Read table rows
            table_rows = notion.blocks.children.list(block_id=block["id"])
            for row in table_rows["results"]:
                if row["type"] == "table_row":
                    cells = row["table_row"]["cells"]
                    row_text = " | ".join(
                        "".join(rt.get("plain_text", "") for rt in cell)
                        for cell in cells
                    )
                    lines.append(f"| {row_text} |")
        elif block_type == "divider":
            lines.append("---")
        elif block_type == "toggle":
            rich_text = block[block_type].get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_text)
            lines.append(f"▶ {text}")
            # Read children of toggle
            children = notion.blocks.children.list(block_id=block["id"])
            for child in children["results"]:
                child_type = child["type"]
                if child_type in ("paragraph", "bulleted_list_item", "code"):
                    if child_type == "code":
                        rt = child[child_type].get("rich_text", [])
                        child_text = "".join(r.get("plain_text", "") for r in rt)
                        lines.append(f"  ```")
                        lines.append(f"  {child_text}")
                        lines.append(f"  ```")
                    else:
                        rt = child[child_type].get("rich_text", [])
                        child_text = "".join(r.get("plain_text", "") for r in rt)
                        lines.append(f"  {child_text}")
        else:
            pass  # Skip unsupported block types

    return "\n".join(lines)


# ─── Google Sheets ────────────────────────────────────────────────

def read_google_sheet(sheet_id: str, range_name: str = "") -> list[list[str]]:
    """Read data from a Google Sheet."""
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "./googlesheet-key.json")
    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)

    # Get all sheet names if no range specified
    if not range_name:
        meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = meta.get("sheets", [])
        all_data = []
        for sheet in sheets:
            title = sheet["properties"]["title"]
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=f"'{title}'"
            ).execute()
            values = result.get("values", [])
            if values:
                all_data.append({"sheet": title, "data": values})
        return all_data
    else:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_name
        ).execute()
        return result.get("values", [])


def list_drive_folder(folder_id: str) -> list[dict]:
    """List files in a Google Drive folder."""
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "./googlesheet-key.json")
    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds)

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)",
        pageSize=100,
    ).execute()
    return results.get("files", [])


# ─── Main ─────────────────────────────────────────────────────────

def main():
    output_dir = Path("agents/data-hancock/.kiro/steering")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Step 1: Reading Notion BQ notes...")
    print("=" * 60)

    notion_page_id = os.getenv("NOTION_BQ_PAGE_ID", "")
    if notion_page_id:
        notion_content = read_notion_page(notion_page_id)
        print(f"  Read {len(notion_content)} chars from Notion")
        # Save raw content
        (output_dir / "notion-bq-notes.md").write_text(
            f"---\ninclusion: always\n---\n\n# BigQuery 資料表筆記（來自 Notion）\n\n{notion_content}",
            encoding="utf-8"
        )
        print(f"  Saved to notion-bq-notes.md")
    else:
        print("  SKIPPED: NOTION_BQ_PAGE_ID not set")
        notion_content = ""

    print()
    print("=" * 60)
    print("Step 2: Reading Query Warehouse...")
    print("=" * 60)

    query_sheet_id = os.getenv("QUERY_WAREHOUSE_SHEET_ID", "")
    if query_sheet_id:
        sheets_data = read_google_sheet(query_sheet_id)
        print(f"  Found {len(sheets_data)} sheet(s)")

        query_lines = []
        for sheet_info in sheets_data:
            title = sheet_info["sheet"]
            data = sheet_info["data"]
            print(f"    Sheet: {title} ({len(data)} rows)")
            query_lines.append(f"\n## Sheet: {title}\n")

            if not data:
                continue

            headers = data[0] if data else []
            query_lines.append(f"Columns: {', '.join(headers)}\n")

            for i, row in enumerate(data[1:], 1):
                if i > 50:  # Limit to first 50 rows
                    query_lines.append(f"\n... ({len(data) - 51} more rows)")
                    break
                row_dict = {}
                for j, val in enumerate(row):
                    if j < len(headers) and val.strip():
                        row_dict[headers[j]] = val.strip()
                if row_dict:
                    query_lines.append(f"\n### Row {i}")
                    for k, v in row_dict.items():
                        if len(v) > 500:
                            query_lines.append(f"**{k}:**\n```sql\n{v}\n```")
                        else:
                            query_lines.append(f"**{k}:** {v}")

        query_content = "\n".join(query_lines)
        (output_dir / "query-warehouse.md").write_text(
            f"---\ninclusion: always\n---\n\n# Query Warehouse（過往 SQL 範例）\n{query_content}",
            encoding="utf-8"
        )
        print(f"  Saved to query-warehouse.md")
    else:
        print("  SKIPPED: QUERY_WAREHOUSE_SHEET_ID not set")

    print()
    print("=" * 60)
    print("Step 3: Listing Schema folder...")
    print("=" * 60)

    schema_folder_id = os.getenv("SCHEMA_FOLDER_ID", "")
    if schema_folder_id:
        files = list_drive_folder(schema_folder_id)
        print(f"  Found {len(files)} files in schema folder:")
        for f in files:
            print(f"    - {f['name']} ({f['mimeType']})")
    else:
        print("  SKIPPED: SCHEMA_FOLDER_ID not set")

    print()
    print("=" * 60)
    print("DONE. Check agents/data-hancock/.kiro/steering/ for output files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
