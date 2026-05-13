"""TelegramAdapter - message routing between Telegram Forum Topics and Agent instances.

Supports:
- Long text messages (auto-split at 4096 chars)
- Photo/image receiving and sending
- Document/file receiving and sending
"""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from dataclasses import dataclass, field

from telegram import Update, Bot
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

from .config import TeamConfig, InstanceConfig

log = logging.getLogger(__name__)

TELEGRAM_MAX_TEXT = 4096


@dataclass
class PendingMedia:
    """Tracks downloaded media files for an instance."""
    instance: str
    file_path: str
    file_type: str  # "photo" | "document"
    caption: str = ""


class TelegramAdapter:
    """Routes Telegram messages to agent instances based on Forum Topic ID."""

    def __init__(self, config: TeamConfig, daemon) -> None:
        self.config = config
        self.daemon = daemon
        self._app: Application | None = None
        self._bot: Bot | None = None
        self._topic_to_instance: dict[int, str] = {}
        self._instance_to_topic: dict[str, int] = {}
        self._media_dir = Path("media")
        self._busy_instances: dict[str, str] = {}  # instance -> task description
        self._build_routing_table()

    def _build_routing_table(self) -> None:
        """Map topic_id <-> instance name."""
        for name, ic in self.config.instances.items():
            if ic.topic_id is not None:
                self._topic_to_instance[ic.topic_id] = name
                self._instance_to_topic[name] = ic.topic_id
        log.info(
            "Routing table: %d topics mapped",
            len(self._topic_to_instance),
        )

    def _is_allowed_user(self, user_id: int) -> bool:
        """Check if user is in the allowed list."""
        if not self.config.access.allowed_users:
            return True  # No restriction if list is empty
        return user_id in self.config.access.allowed_users

    def _resolve_instance(self, update: Update) -> str | None:
        """Determine which instance should handle this message."""
        msg = update.effective_message
        if not msg:
            return None

        thread_id = msg.message_thread_id
        if thread_id and thread_id in self._topic_to_instance:
            return self._topic_to_instance[thread_id]

        # General topic -> find instance with general_topic=True
        for name, ic in self.config.instances.items():
            if ic.general_topic:
                return name
        return None

    async def start(self) -> None:
        """Start the Telegram bot polling."""
        token = os.environ.get(self.config.channel.bot_token_env, "")
        if not token:
            log.error(
                "Bot token not found in env var: %s",
                self.config.channel.bot_token_env,
            )
            return

        self._media_dir.mkdir(parents=True, exist_ok=True)

        self._app = (
            Application.builder()
            .token(token)
            .build()
        )
        self._bot = self._app.bot

        # Register handlers
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text)
        )
        self._app.add_handler(
            MessageHandler(filters.COMMAND, self._on_command)
        )
        self._app.add_handler(
            MessageHandler(filters.PHOTO, self._on_photo)
        )
        self._app.add_handler(
            MessageHandler(filters.Document.ALL, self._on_document)
        )

        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        log.info("Telegram bot started polling")

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
            log.info("Telegram bot stopped")

    # ─── Incoming message handlers ───────────────────────────────

    # Available models for /mode switching
    AVAILABLE_MODELS: dict[str, str] = {
        "sonnet": "claude-sonnet-4",
        "opus": "claude-opus-4.6",
        "haiku": "claude-haiku-4.5",
    }

    async def _on_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming /commands (Telegram filters these separately from text)."""
        user = update.effective_user
        if not user or not self._is_allowed_user(user.id):
            return

        instance = self._resolve_instance(update)
        if not instance:
            return

        text = update.effective_message.text or ""
        log.info(
            "[cmd] %s -> %s: %s",
            user.username or user.id,
            instance,
            text[:80],
        )

        # Strip @botname suffix if present (e.g. /help@rd7_test123_bot)
        cmd_text = text.split("@")[0] if "@" in text.split()[0] else text

        handled = await self._handle_slash_command(instance, cmd_text)
        if not handled:
            # Unknown command, forward to agent as regular text
            import asyncio
            asyncio.create_task(self._process_and_reply(instance, text))

    async def _on_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming text messages."""
        user = update.effective_user
        if not user or not self._is_allowed_user(user.id):
            return

        instance = self._resolve_instance(update)
        if not instance:
            return

        text = update.effective_message.text or ""
        log.info(
            "[text] %s -> %s: %s",
            user.username or user.id,
            instance,
            text[:80],
        )

        # Handle slash commands locally (don't forward to agent)
        if text.startswith("/"):
            handled = await self._handle_slash_command(instance, text)
            if handled:
                return

        # If instance is busy, immediately respond with status
        if instance in self._busy_instances:
            task_desc = self._busy_instances[instance]
            state = self.daemon.instances.get(instance)
            hint = ""
            if state and state.process and state.process._pending_response:
                last = state.process._pending_response[-1][:60]
                if last and not last.startswith(("{", '"', "[")):
                    hint = f"\n📝 最新進度：{last}"
            await self.send_text(
                instance,
                f"🔄 目前正在處理：{task_desc}...{hint}\n\n"
                f"⏳ 請等目前任務完成後再發送新指令。",
            )
            return

        # Process in background to avoid blocking other messages
        import asyncio
        asyncio.create_task(self._process_and_reply(instance, text))

    async def _handle_slash_command(self, instance: str, text: str) -> bool:
        """Handle slash commands. Returns True if handled."""
        parts = text.strip().split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "/help":
            help_text = (
                "📋 可用指令：\n\n"
                "/mode <model> — 切換 AI 模型\n"
                "/mode — 顯示目前使用的模型\n"
                "/help — 顯示此說明\n\n"
                "🤖 可用模型：\n"
                "• opus → claude-opus-4.6（預設，最強）\n"
                "• sonnet → claude-sonnet-4（快速平衡）\n"
                "• haiku → claude-haiku-4.5（最快，輕量）\n\n"
                "範例：/mode sonnet"
            )
            await self.send_text(instance, help_text)
            return True

        elif cmd == "/mode":
            if len(parts) < 2:
                # Show current model
                state = self.daemon.instances.get(instance)
                current = state.config.model if state else "unknown"
                await self.send_text(
                    instance,
                    f"🤖 目前模型：{current or 'claude-sonnet-4'}\n\n"
                    f"可切換：sonnet / opus / haiku\n"
                    f"用法：/mode <model>",
                )
                return True

            model_key = parts[1].strip().lower()
            if model_key not in self.AVAILABLE_MODELS:
                await self.send_text(
                    instance,
                    f"⚠️ 未知模型：{model_key}\n\n"
                    f"可用模型：sonnet / opus / haiku",
                )
                return True

            target_model = self.AVAILABLE_MODELS[model_key]
            await self.send_text(instance, f"🔄 切換模型至 {target_model}，重啟中...")

            success = await self.daemon.restart_with_model(instance, target_model)
            if success:
                await self.send_text(instance, f"✅ 已切換至 {target_model}")
            else:
                await self.send_text(instance, f"❌ 切換失敗，請稍後再試")
            return True

        return False

    async def _process_and_reply(self, instance: str, text: str) -> None:
        """Send message to agent and wait for completion (non-blocking).

        Features:
        - Every 60s sends progress update to user
        - If new message arrives while busy, immediately responds with status
        - Agent can use reply() MCP tool to send directly
        """
        try:
            # Flatten multi-line text to single line for kiro-cli stdin
            flat_text = text.replace("\n", " ↵ ").replace("\r", "")

            log.info("[send] -> %s: %s", instance, flat_text[:120])

            # Mark instance as busy
            self._busy_instances[instance] = text[:50]

            # Send immediate acknowledgment for file/image uploads
            if "[FILE:" in text or "[IMAGE:" in text:
                await self.send_text(instance, "🔄 收到檔案，處理中...")

            # Record incoming user message
            if hasattr(self.daemon, '_api_ref') and self.daemon._api_ref:
                from .api import ConversationMessage
                self.daemon._api_ref.conversations.add(instance, ConversationMessage(
                    role="user",
                    text=text,
                ))

            # Start progress reporter task
            progress_task = asyncio.create_task(
                self._progress_reporter(instance)
            )

            try:
                response = await self.daemon.send_message(instance, flat_text)
            finally:
                progress_task.cancel()
                self._busy_instances.pop(instance, None)

            log.info("[resp] <- %s: %s", instance, (response or "(none)")[:120])

            if response and not self._agent_already_replied(response):
                if hasattr(self.daemon, '_api_ref') and self.daemon._api_ref:
                    from .api import ConversationMessage
                    self.daemon._api_ref.conversations.add(instance, ConversationMessage(
                        role="agent",
                        text=response,
                    ))
                await self.send_text(instance, response)
            elif not response:
                log.warning("No response from %s (timeout or empty)", instance)
                await self.send_text(instance, "⚠️ 處理超時，請稍後再試")
        except Exception as e:
            self._busy_instances.pop(instance, None)
            log.error("Error processing message for %s: %s", instance, e, exc_info=True)
            await self.send_text(instance, f"❌ 處理錯誤：{e}")

    async def _progress_reporter(self, instance: str) -> None:
        """Send progress updates every 60 seconds while agent is working."""
        elapsed = 0
        try:
            while True:
                await asyncio.sleep(60)
                elapsed += 1
                # Get latest buffered line from process
                state = self.daemon.instances.get(instance)
                hint = ""
                if state and state.process and state.process._pending_response:
                    last_line = state.process._pending_response[-1][:60]
                    # Clean up the hint
                    if last_line and not last_line.startswith(("{", '"', "[")):
                        hint = f"\n📝 {last_line}"
                await self.send_text(
                    instance,
                    f"🔄 仍在處理中...（已經過 {elapsed} 分鐘）{hint}",
                )
        except asyncio.CancelledError:
            pass

    @staticmethod
    def _agent_already_replied(response: str) -> bool:
        """Check if the response indicates agent used reply tool (already sent)."""
        # If the response is mostly tool-call noise or empty after filtering,
        # the agent likely used reply() to send directly
        stripped = response.strip()
        if not stripped:
            return True
        # If response contains only tool execution artifacts
        if stripped in ("sent", "photo sent", "document sent"):
            return True
        return False

    async def _on_photo(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming photos - download and forward path to agent."""
        user = update.effective_user
        if not user or not self._is_allowed_user(user.id):
            return

        instance = self._resolve_instance(update)
        if not instance:
            return

        msg = update.effective_message
        # Get highest resolution photo
        photo = msg.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # Download to media directory
        inst_dir = self._media_dir / instance
        inst_dir.mkdir(parents=True, exist_ok=True)
        local_path = inst_dir / f"{photo.file_unique_id}.jpg"
        await file.download_to_drive(str(local_path))

        caption = msg.caption or ""
        # Use absolute path so agent can find the file regardless of CWD
        abs_path = local_path.resolve()
        payload = f"[IMAGE: {abs_path}]"
        if caption:
            payload += f" | {caption}"

        log.info("[photo] %s -> %s: %s", user.username, instance, local_path)
        import asyncio
        asyncio.create_task(self._process_and_reply(instance, payload))

    async def _on_document(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle incoming documents - download and forward path to agent."""
        user = update.effective_user
        if not user or not self._is_allowed_user(user.id):
            return

        instance = self._resolve_instance(update)
        if not instance:
            return

        msg = update.effective_message
        doc = msg.document
        file = await context.bot.get_file(doc.file_id)

        inst_dir = self._media_dir / instance
        inst_dir.mkdir(parents=True, exist_ok=True)
        filename = doc.file_name or f"{doc.file_unique_id}"
        local_path = inst_dir / filename
        await file.download_to_drive(str(local_path))

        caption = msg.caption or ""
        # Use absolute path so agent can find the file regardless of CWD
        abs_path = local_path.resolve()
        payload = f"[FILE: {abs_path}] (name={filename}, size={doc.file_size})"
        if caption:
            payload += f" | {caption}"

        log.info("[doc] %s -> %s: %s", user.username, instance, filename)
        import asyncio
        asyncio.create_task(self._process_and_reply(instance, payload))

    # ─── Topic management ────────────────────────────────────────

    async def create_forum_topic(self, name: str) -> dict:
        """Create a new Forum Topic in the Telegram group.

        Returns dict with topic_id and name on success.
        """
        if not self._bot:
            return {"ok": False, "error": "Bot not initialized"}

        chat_id = self.config.channel.group_id
        if not chat_id:
            return {"ok": False, "error": "No group_id configured"}

        try:
            topic = await self._bot.create_forum_topic(
                chat_id=chat_id,
                name=name,
            )
            topic_id = topic.message_thread_id
            log.info("[topic] Created forum topic: %s (id=%d)", name, topic_id)
            return {"ok": True, "topic_id": topic_id, "name": name}
        except Exception as e:
            log.error("Failed to create forum topic '%s': %s", name, e)
            return {"ok": False, "error": str(e)}

    def add_topic_mapping(self, instance: str, topic_id: int) -> None:
        """Add a new instance <-> topic mapping at runtime."""
        self._topic_to_instance[topic_id] = instance
        self._instance_to_topic[instance] = topic_id
        log.info("[routing] Added mapping: %s <-> topic %d", instance, topic_id)

    # ─── Outgoing message methods (called by API/MCP) ────────────

    async def send_text(
        self,
        instance: str,
        text: str,
        parse_mode: str | None = None,
    ) -> bool:
        """Send text to the Telegram topic for this instance.

        Auto-splits messages longer than 4096 chars.
        """
        if not self._bot:
            log.warning("Bot not initialized, cannot send")
            return False

        topic_id = self._instance_to_topic.get(instance)
        chat_id = self.config.channel.group_id
        if not chat_id:
            return False

        chunks = self._split_text(text)
        for chunk in chunks:
            try:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    message_thread_id=topic_id,
                    parse_mode=parse_mode,
                )
            except Exception as e:
                log.error("Failed to send text to %s: %s", instance, e)
                # Retry without parse_mode if formatting failed
                if parse_mode:
                    try:
                        await self._bot.send_message(
                            chat_id=chat_id,
                            text=chunk,
                            message_thread_id=topic_id,
                        )
                    except Exception as e2:
                        log.error("Retry also failed: %s", e2)
                        return False
                else:
                    return False
        return True

    async def send_photo(
        self,
        instance: str,
        photo_path: str,
        caption: str = "",
    ) -> bool:
        """Send a photo to the Telegram topic for this instance."""
        if not self._bot:
            return False

        topic_id = self._instance_to_topic.get(instance)
        chat_id = self.config.channel.group_id
        if not chat_id:
            return False

        path = Path(photo_path)
        if not path.exists():
            log.error("Photo not found: %s", photo_path)
            return False

        try:
            with open(path, "rb") as f:
                await self._bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=caption[:1024] if caption else None,
                    message_thread_id=topic_id,
                )
            return True
        except Exception as e:
            log.error("Failed to send photo to %s: %s", instance, e)
            return False

    async def send_document(
        self,
        instance: str,
        file_path: str,
        caption: str = "",
    ) -> bool:
        """Send a document/file to the Telegram topic for this instance."""
        if not self._bot:
            return False

        topic_id = self._instance_to_topic.get(instance)
        chat_id = self.config.channel.group_id
        if not chat_id:
            return False

        path = Path(file_path)
        if not path.exists():
            log.error("File not found: %s", file_path)
            return False

        try:
            with open(path, "rb") as f:
                await self._bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename=path.name,
                    caption=caption[:1024] if caption else None,
                    message_thread_id=topic_id,
                )
            return True
        except Exception as e:
            log.error("Failed to send document to %s: %s", instance, e)
            return False

    # ─── Utilities ───────────────────────────────────────────────

    @staticmethod
    def _split_text(text: str) -> list[str]:
        """Split text into chunks of max TELEGRAM_MAX_TEXT chars.

        Tries to split at newlines, then at spaces, then hard-cut.
        """
        if len(text) <= TELEGRAM_MAX_TEXT:
            return [text]

        chunks: list[str] = []
        remaining = text

        while remaining:
            if len(remaining) <= TELEGRAM_MAX_TEXT:
                chunks.append(remaining)
                break

            # Try to find a good split point
            cut = TELEGRAM_MAX_TEXT
            # Prefer splitting at newline
            nl_pos = remaining.rfind("\n", 0, cut)
            if nl_pos > cut // 2:
                cut = nl_pos + 1
            else:
                # Try splitting at space
                sp_pos = remaining.rfind(" ", 0, cut)
                if sp_pos > cut // 2:
                    cut = sp_pos + 1

            chunks.append(remaining[:cut])
            remaining = remaining[cut:]

        return chunks
