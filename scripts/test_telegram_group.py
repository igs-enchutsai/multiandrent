"""Test if bot can access the configured Telegram group."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import yaml


async def test_group() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)

    # Load team.yaml
    team_path = Path(__file__).parent.parent / "team.yaml"
    with open(team_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    group_id = config.get("channel", {}).get("group_id", 0)
    print(f"Group ID from team.yaml: {group_id}")

    from telegram import Bot
    bot = Bot(token=token)

    try:
        chat = await bot.get_chat(chat_id=group_id)
        print(f"\n✓ 群組連線成功!")
        print(f"  Chat Title:  {chat.title}")
        print(f"  Chat Type:   {chat.type}")
        print(f"  Is Forum:    {chat.is_forum}")
        print(f"  Chat ID:     {chat.id}")
    except Exception as e:
        print(f"\n✗ 無法存取群組: {e}")
        print("\n可能原因:")
        print("  1. Bot 尚未加入該群組")
        print("  2. group_id 不正確")
        print("  3. Bot 沒有管理員權限")
        print("\n請用 scripts/get_ids.py 取得正確的 group_id")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_group())
