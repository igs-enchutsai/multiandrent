"""Query BigQuery tables to get actual column schemas using INFORMATION_SCHEMA + sample data.

Rules:
- WHERE BQDate = CURRENT_DATE('Asia/Taipei') - INTERVAL 1 DAY
- LIMIT 100
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2.service_account import Credentials

load_dotenv()

# Datasets to scan for table schemas
DATASETS = ["bklog", "preprocessed_bklog", "DailyDimData", "kuochinfu"]

# Tables we specifically want to sample (from Notion notes)
SAMPLE_TABLES = [
    "rd7-data-big-query.bklog.BattlePassBuyLog",
    "rd7-data-big-query.bklog.ActivityMissionRewardLog",
    "rd7-data-big-query.bklog.ActivityMissionCompleteLog",
    "rd7-data-big-query.DailyDimData.ActivityMissionDimLog",
    "rd7-data-big-query.preprocessed_bklog.DailyUserInfoSnapshot",
    "rd7-data-big-query.bklog.SessionActive",
    "rd7-data-big-query.bklog.SessionTigerSharkBetWinLog",
    "rd7-data-big-query.preprocessed_bklog.DailyUserFishMetrics",
    "rd7-data-big-query.bklog.GameConsume",
    "rd7-data-big-query.bklog.RankSettlementLog",
    "rd7-data-big-query.bklog.DimActivityRankLog",
    "rd7-data-big-query.bklog.SessionItemLog",
    "rd7-data-big-query.kuochinfu.watchlist",
    "rd7-data-big-query.bklog.ActivityMissionPopUpStateLog",
    "rd7-data-big-query.DailyDimData.DailyDimItemValue",
    "rd7-data-big-query.bklog.ExchangeActivityExchangeLog",
    "rd7-data-big-query.bklog.ExchangeActivityDetailLog",
    "rd7-data-big-query.kuochinfu.NewNESockPuppetUserLog",
    "rd7-data-big-query.preprocessed_bklog.UserOperationGroup",
]


def main():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json")
    creds = Credentials.from_service_account_file(creds_path)
    client = bigquery.Client(credentials=creds, project="rd7-data-big-query")

    output_dir = Path("agents/data-hancock/.kiro/steering")
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = ["---\ninclusion: always\n---\n", "# BigQuery 資料表 Schema（實際查詢結果）\n"]
    lines.append("查詢條件：BQDate = CURRENT_DATE('Asia/Taipei') - 1 day, LIMIT 100\n")

    success_count = 0
    error_count = 0

    for table_ref in SAMPLE_TABLES:
        print(f"\nQuerying: {table_ref}...")
        parts = table_ref.split(".")
        if len(parts) != 3:
            print(f"  ❌ Invalid table reference")
            continue

        # Step 1: Get schema via API
        try:
            table = client.get_table(table_ref)
            schema_fields = table.schema
            print(f"  Schema: {len(schema_fields)} columns, ~{table.num_rows} rows total")

            lines.append(f"\n## `{table_ref}`")
            lines.append(f"總行數約 {table.num_rows:,} | 分區: {table.time_partitioning.field if table.time_partitioning else 'None'}\n")
            lines.append("| 欄位 | 類型 | 模式 | 說明 |")
            lines.append("|------|------|------|------|")
            for field in schema_fields:
                desc = field.description or ""
                lines.append(f"| {field.name} | {field.field_type} | {field.mode} | {desc[:60]} |")

            # Step 2: Sample query
            try:
                query = f"""
                SELECT *
                FROM `{table_ref}`
                WHERE BQDate = CURRENT_DATE('Asia/Taipei') - INTERVAL 1 DAY
                LIMIT 5
                """
                df = client.query(query).to_dataframe()
                if len(df) > 0:
                    lines.append(f"\n**Sample (5 rows):**\n```")
                    lines.append(df.to_string(max_colwidth=40))
                    lines.append("```")
                    print(f"  ✅ Sample: {len(df)} rows")
                else:
                    # Try without BQDate filter
                    query2 = f"SELECT * FROM `{table_ref}` LIMIT 5"
                    df = client.query(query2).to_dataframe()
                    if len(df) > 0:
                        lines.append(f"\n**Sample (5 rows, no date filter):**\n```")
                        lines.append(df.to_string(max_colwidth=40))
                        lines.append("```")
                        print(f"  ✅ Sample (no date filter): {len(df)} rows")
            except Exception as e:
                # Partition required error - try without date filter
                try:
                    query2 = f"SELECT * FROM `{table_ref}` WHERE BQDate >= CURRENT_DATE('Asia/Taipei') - INTERVAL 2 DAY LIMIT 5"
                    df = client.query(query2).to_dataframe()
                    if len(df) > 0:
                        lines.append(f"\n**Sample (5 rows):**\n```")
                        lines.append(df.to_string(max_colwidth=40))
                        lines.append("```")
                        print(f"  ✅ Sample: {len(df)} rows")
                except Exception as e2:
                    print(f"  ⚠️ Sample failed: {str(e2)[:100]}")

            success_count += 1

        except Exception as e:
            error_msg = str(e)[:150]
            lines.append(f"\n## `{table_ref}`")
            lines.append(f"❌ 錯誤: {error_msg}")
            error_count += 1
            print(f"  ❌ {error_msg}")

    # Summary
    lines.insert(3, f"成功：{success_count} 張表 | 失敗：{error_count} 張表\n")

    schema_content = "\n".join(lines)
    output_path = output_dir / "bq-table-schemas.md"
    output_path.write_text(schema_content, encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"Done! Saved to {output_path}")
    print(f"Success: {success_count} | Failed: {error_count}")


if __name__ == "__main__":
    main()
