"""Team manager - high-level multi-instance orchestration."""
from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
import time
from pathlib import Path

from .config import TeamConfig, get_home, load_team_config
from .daemon import Daemon
from .telegram_adapter import TelegramAdapter

log = logging.getLogger(__name__)


class TeamManager:
    def __init__(self, config: TeamConfig) -> None:
        self.config = config
        self.daemon = Daemon(config)
        self.telegram: TelegramAdapter | None = None
        self._started_at: float = 0

    async def start(self) -> dict[str, bool]:
        self._started_at = time.time()
        log.info("Starting team (%d instances)...", len(self.config.instances))
        results = await self.daemon.start_all()
        ok = sum(1 for v in results.values() if v)
        log.info("Team ready: %d/%d running", ok, len(results))

        # Start Telegram adapter
        self.telegram = TelegramAdapter(self.config, self.daemon)
        await self.telegram.start()

        return results

    async def stop(self) -> None:
        if self.telegram:
            await self.telegram.stop()
        await self.daemon.stop_all()

    def status(self) -> dict:
        instances = self.daemon.get_status()
        running = sum(1 for i in instances if i["status"] == "running")
        return {"uptime": time.time() - self._started_at, "total": len(instances), "running": running, "instances": instances}


async def run_team(config_path: Path | None = None) -> None:
    """Main entry point - load config, start team, handle signals."""
    env_file = get_home() / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    config = load_team_config(config_path)
    manager = TeamManager(config)
    stop_event = asyncio.Event()

    # Write PID
    pid_file = get_home() / "team.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))

    try:
        await manager.start()

        # Start API
        from .api import DaemonAPI
        api = DaemonAPI(manager.daemon, manager.telegram)
        # Wire API ref so telegram adapter can record conversations
        manager.daemon._api_ref = api
        await api.start(port=config.health_port)
        log.info("API started on port %d", config.health_port)

        # Send startup greeting to all running agents
        asyncio.create_task(_send_startup_greetings(manager))

        # Main loop
        if sys.platform == "win32":
            while not stop_event.is_set():
                await asyncio.sleep(1)
        else:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, stop_event.set)
            await stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        await manager.stop()
        pid_file.unlink(missing_ok=True)


async def _send_startup_greetings(manager: TeamManager) -> None:
    """After startup, ask each agent to report status and unfinished work."""
    await asyncio.sleep(3)  # Wait for API and Telegram to be fully ready

    startup_prompt = (
        "系統剛重啟完成。請用 reply() 工具回報：\n"
        "1. 你的身份和職責（一句話）\n"
        "2. 上次未完成的工作（如果有的話）\n"
        "3. 是否需要用戶指示才能繼續\n"
        "格式簡潔，不超過 200 字。"
    )

    for name, state in manager.daemon.instances.items():
        if state.status.value == "running" and state.process:
            try:
                log.info("Sending startup greeting to %s", name)
                # Mark as busy in telegram adapter
                if manager.telegram:
                    manager.telegram._busy_instances[name] = "啟動回報"
                response = await manager.daemon.send_message(name, startup_prompt)
                if manager.telegram:
                    manager.telegram._busy_instances.pop(name, None)
                # If agent didn't use reply tool, send response via telegram
                if response and response.strip() not in ("", "sent"):
                    if manager.telegram:
                        await manager.telegram.send_text(name, response)
            except Exception as e:
                log.warning("Startup greeting failed for %s: %s", name, e)
                if manager.telegram:
                    manager.telegram._busy_instances.pop(name, None)
