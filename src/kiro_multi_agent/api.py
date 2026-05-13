"""FastAPI REST API for cross-agent communication."""
from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """A single message in conversation history."""
    role: str  # "user" | "agent"
    text: str
    timestamp: float = field(default_factory=time.time)
    media_path: str | None = None
    media_type: str | None = None  # "photo" | "document"


class ConversationStore:
    """In-memory conversation history per instance."""

    def __init__(self, max_per_instance: int = 200) -> None:
        self._store: dict[str, deque[ConversationMessage]] = {}
        self._max = max_per_instance

    def add(self, instance: str, msg: ConversationMessage) -> None:
        if instance not in self._store:
            self._store[instance] = deque(maxlen=self._max)
        self._store[instance].append(msg)

    def get(self, instance: str, limit: int = 20) -> list[dict]:
        msgs = self._store.get(instance, deque())
        recent = list(msgs)[-limit:]
        return [
            {
                "role": m.role,
                "text": m.text,
                "timestamp": time.strftime("%H:%M:%S", time.localtime(m.timestamp)),
                "media_path": m.media_path,
                "media_type": m.media_type,
            }
            for m in recent
        ]


# ─── Pydantic models (module-level for FastAPI + __future__ annotations) ─────

_pydantic_available = False
try:
    from pydantic import BaseModel
    _pydantic_available = True
except ImportError:
    pass

if _pydantic_available:
    class SendRequest(BaseModel):
        instance: str
        message: str
        source: str = ""

    class ReplyRequest(BaseModel):
        instance: str
        text: str
        kind: str = "primary"

    class LogRequest(BaseModel):
        instance: str
        text: str

    class PhotoRequest(BaseModel):
        instance: str
        photo_path: str
        caption: str = ""

    class DocumentRequest(BaseModel):
        instance: str
        file_path: str
        caption: str = ""

    class ModelSwitchRequest(BaseModel):
        instance: str
        model: str

    class CreateTopicRequest(BaseModel):
        name: str
        instance: str = ""


class DaemonAPI:
    """Lightweight HTTP API wrapping the Daemon for MCP tool calls."""

    def __init__(self, daemon, telegram=None) -> None:
        self.daemon = daemon
        self.telegram = telegram
        self.conversations = ConversationStore()
        self._server = None

    async def start(self, port: int = 8470) -> None:
        try:
            import uvicorn
            from fastapi import FastAPI, Query
        except ImportError:
            log.warning("FastAPI/uvicorn not installed, API disabled")
            return

        if not _pydantic_available:
            log.warning("Pydantic not installed, API disabled")
            return

        app = FastAPI(title="Kiro Multi-Agent API")
        telegram = self.telegram
        conversations = self.conversations

        @app.get("/api/status")
        async def status():
            return {"ok": True, "instances": self.daemon.get_status()}

        @app.post("/api/send")
        async def send(req: SendRequest):
            # Record outgoing message in conversation
            conversations.add(req.instance, ConversationMessage(
                role="leader" if req.source else "user",
                text=req.message,
            ))
            response = await self.daemon.send_message(req.instance, req.message)
            if response:
                conversations.add(req.instance, ConversationMessage(
                    role="agent",
                    text=response,
                ))
            return {"ok": response is not None, "response": response}

        @app.post("/api/reply")
        async def reply(req: ReplyRequest):
            # Record agent reply in conversation
            conversations.add(req.instance, ConversationMessage(
                role="agent",
                text=req.text,
            ))
            if telegram:
                ok = await telegram.send_text(req.instance, req.text)
                return {"ok": ok}
            log.info("[reply] %s: %s", req.instance, req.text[:100])
            return {"ok": True}

        @app.post("/api/reply/photo")
        async def reply_photo(req: PhotoRequest):
            conversations.add(req.instance, ConversationMessage(
                role="agent",
                text=req.caption or "[photo]",
                media_path=req.photo_path,
                media_type="photo",
            ))
            if telegram:
                ok = await telegram.send_photo(
                    req.instance, req.photo_path, req.caption
                )
                return {"ok": ok}
            return {"ok": False, "error": "Telegram not connected"}

        @app.post("/api/reply/document")
        async def reply_document(req: DocumentRequest):
            conversations.add(req.instance, ConversationMessage(
                role="agent",
                text=req.caption or "[document]",
                media_path=req.file_path,
                media_type="document",
            ))
            if telegram:
                ok = await telegram.send_document(
                    req.instance, req.file_path, req.caption
                )
                return {"ok": ok}
            return {"ok": False, "error": "Telegram not connected"}

        @app.post("/api/log")
        async def log_msg(req: LogRequest):
            log.info("[log] %s: %s", req.instance, req.text[:200])
            return {"ok": True}

        @app.post("/api/progress")
        async def progress(req: dict[str, Any]):
            log.info("[progress] %s: %s", req.get("instance"), req.get("message"))
            return {"ok": True}

        @app.get("/api/conversation/{instance}")
        async def get_conversation(instance: str, limit: int = Query(default=20)):
            messages = conversations.get(instance, limit)
            return {"ok": True, "messages": messages}

        @app.get("/api/media/{instance}")
        async def list_media(instance: str):
            from pathlib import Path
            media_dir = Path("media") / instance
            if not media_dir.exists():
                return {"ok": True, "files": []}
            files = []
            for f in sorted(media_dir.iterdir()):
                if f.is_file():
                    size_kb = f.stat().st_size / 1024
                    files.append(f"{f.name} ({size_kb:.1f} KB)")
            return {"ok": True, "files": files}

        @app.post("/api/model/switch")
        async def switch_model(req: ModelSwitchRequest):
            success = await self.daemon.restart_with_model(req.instance, req.model)
            return {"ok": success, "model": req.model}

        @app.get("/api/model/{instance}")
        async def get_model(instance: str):
            state = self.daemon.instances.get(instance)
            if not state:
                return {"ok": False, "error": "instance not found"}
            return {"ok": True, "model": state.config.model or "claude-opus-4"}

        @app.post("/api/topic/create")
        async def create_topic(req: CreateTopicRequest):
            if not telegram:
                return {"ok": False, "error": "Telegram not connected"}
            result = await telegram.create_forum_topic(req.name)
            if result.get("ok") and req.instance:
                # Auto-map the new topic to the instance
                telegram.add_topic_mapping(req.instance, result["topic_id"])
            return result

        @app.post("/api/team/restart")
        async def restart_team():
            """Reload config and restart all instances."""
            results = await self.daemon.reload_config_and_restart()
            # Rebuild telegram routing table
            if telegram:
                telegram.config = self.daemon.config
                telegram._topic_to_instance.clear()
                telegram._instance_to_topic.clear()
                telegram._build_routing_table()
            running = sum(1 for v in results.values() if v)
            return {
                "ok": running > 0,
                "total": len(results),
                "running": running,
                "instances": {k: "running" if v else "failed" for k, v in results.items()},
            }

        @app.post("/api/team/full-restart")
        async def full_restart_team():
            """Full daemon restart - reload Python code and restart everything."""
            import os
            import sys

            # Stop all instances first
            await self.daemon.stop_all()
            if telegram:
                try:
                    await telegram.stop()
                except Exception:
                    pass

            # Schedule the actual restart after response is sent
            async def _do_restart():
                await asyncio.sleep(1)
                python = sys.executable
                args = [python, "-m", "kiro_multi_agent", "team", "start"]
                log.info("Full restart: exec %s", " ".join(args))
                os.execv(python, args)

            asyncio.create_task(_do_restart())
            return {"ok": True, "message": "Full daemon restart initiated"}

        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        self._server = uvicorn.Server(config)
        asyncio.create_task(self._server.serve())

    async def stop(self) -> None:
        if self._server:
            self._server.should_exit = True
