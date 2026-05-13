"""Test Telegram Bot connection - verify token is valid and bot can reach API."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


async def test_bot() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    print(f"Token: {token[:10]}...{token[-5:]}")
    print("Testing Telegram Bot API connection...")

    from telegram import Bot
    bot = Bot(token=token)

    try:
        me = await bot.get_me()
        print(f"\n✓ Bot 連線成功!")
        print(f"  Bot Name:     {me.first_name}")
        print(f"  Bot Username: @{me.username}")
        print(f"  Bot ID:       {me.id}")
        print(f"  Can Join Groups: {me.can_join_groups}")
        print(f"  Can Read Messages: {me.can_read_all_group_messages}")
    except Exception as e:
        print(f"\n✗ Bot 連線失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_bot())
