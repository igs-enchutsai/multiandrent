"""Temporary script to get Telegram group_id, topic_id, and user_id."""
from __future__ import annotations

import asyncio
import json
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def on_message(update: Update, context) -> None:
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    # Try multiple ways to get topic/thread id
    thread_id = None
    if msg:
        thread_id = getattr(msg, "message_thread_id", None)

    print("=" * 50)
    print(f"  Chat ID (group_id):    {chat.id}")
    print(f"  Chat Title:            {chat.title}")
    print(f"  Chat Type:             {chat.type}")
    print(f"  Is Forum:              {getattr(chat, 'is_forum', None)}")
    print(f"  Topic ID (thread_id):  {thread_id}")
    print(f"  User ID:               {user.id}")
    print(f"  Username:              @{user.username}")
    print(f"  Message:               {msg.text if msg else None}")
    print("=" * 50)
    print()


def main() -> None:
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in .env")
        return

    print("Listening for messages... Send a message in a Forum Topic.")
    print("Press Ctrl+C to stop.\n")

    import asyncio

    async def _run():
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.ALL, on_message))
        async with app:
            await app.start()
            await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            print("Polling started. Waiting for messages...")
            try:
                while True:
                    await asyncio.sleep(1)
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass
            finally:
                await app.updater.stop()
                await app.stop()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
