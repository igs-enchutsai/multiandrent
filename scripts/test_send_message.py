"""Test sending a message to the Leader Topic via Telegram Bot."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import yaml


async def test_send() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)

    # Load team.yaml
    team_path = Path(__file__).parent.parent / "team.yaml"
    with open(team_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    group_id = config["channel"]["group_id"]
    leader_topic_id = config["instances"]["leader-agent"]["topic_id"]

    from telegram import Bot
    bot = Bot(token=token)

    try:
        msg = await bot.send_message(
            chat_id=group_id,
            text="✓ Kiro Multi-Agent 初始化完成！Bot 連線正常。",
            message_thread_id=leader_topic_id,
        )
        print(f"✓ 訊息發送成功! message_id={msg.message_id}")
    except Exception as e:
        print(f"✗ 發送失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_send())
