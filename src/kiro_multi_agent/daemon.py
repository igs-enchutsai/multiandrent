"""Daemon core - instance lifecycle, health monitoring, message delivery."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum

from .config import TeamConfig, InstanceConfig, get_home
from .process import ManagedProcess, register, unregister
from .backend import KiroBackend, KiroBackendConfig

log = logging.getLogger(__name__)


class InstanceStatus(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    CRASHED = "crashed"
    PAUSED = "paused"


@dataclass
class InstanceState:
    config: InstanceConfig
    status: InstanceStatus = InstanceStatus.STOPPED
    process: ManagedProcess | None = None
    crash_count: int = 0
    last_activity: float = 0


class Daemon:
    """Manages the lifecycle of all Kiro CLI instances."""

    def __init__(self, config: TeamConfig) -> None:
        self.config = config
        self.instances: dict[str, InstanceState] = {}
        self._health_tasks: dict[str, asyncio.Task] = {}
        self._api_ref = None  # Set by team.py after API starts
        self.on_hang_detected = None

    async def start_instance(self, name: str) -> None:
        ic = self.config.instances.get(name)
        if not ic:
            raise ValueError(f"Unknown instance: {name}")

        state = self.instances.get(name)
        if state and state.status == InstanceStatus.RUNNING:
            return

        if not state:
            state = InstanceState(config=ic)
            self.instances[name] = state

        state.status = InstanceStatus.STARTING

        # Build Kiro CLI command and start
        backend = KiroBackend()
        cfg = KiroBackendConfig(
            working_directory=ic.working_directory,
            instance_name=name,
            model=ic.model,
            team_api_port=self.config.health_port,
            role=ic.role,
        )
        backend.write_config(cfg)

        mp = ManagedProcess(name=name)
        cmd = backend.build_command(cfg)
        cwd = os.path.abspath(ic.working_directory)
        log.info("Starting %s: cmd=%s cwd=%s", name, cmd[:80], cwd)
        await mp.start(cmd, cwd=cwd)
        register(mp)

        state.process = mp
        ready = await self._wait_for_ready(state)
        if ready:
            state.status = InstanceStatus.RUNNING
            state.last_activity = time.time()
            log.info("Instance %s is ready (pid=%s)", name, mp.pid)
            self._health_tasks[name] = asyncio.create_task(self._health_loop(name))
        else:
            state.status = InstanceStatus.CRASHED
            output = mp.capture(lines=10)
            log.error("Instance %s failed to start. Last output: %s", name, output[-300:] if output else "(empty)")

    async def stop_instance(self, name: str) -> None:
        state = self.instances.get(name)
        if not state or state.status == InstanceStatus.STOPPED:
            return
        if state.process:
            await state.process.kill()
            unregister(name)
        task = self._health_tasks.pop(name, None)
        if task:
            task.cancel()
        state.status = InstanceStatus.STOPPED
        log.info("Instance %s stopped", name)

    async def send_message(self, name: str, text: str) -> str | None:
        """Send message to instance and wait for response."""
        state = self.instances.get(name)
        if not state or state.status != InstanceStatus.RUNNING or not state.process:
            return None
        state.process._on_output = True  # Enable response collection
        await state.process.send_input(text)
        state.last_activity = time.time()
        # Wait for response
        response = await state.process.wait_response(timeout=900)
        return response if response else None

    async def restart_with_model(self, name: str, model: str) -> bool:
        """Restart an instance with a different model."""
        ic = self.config.instances.get(name)
        if not ic:
            return False
        # Update the model in config
        ic.model = model
        # Stop and restart
        await self.stop_instance(name)
        # Reset crash count so it starts fresh
        state = self.instances.get(name)
        if state:
            state.crash_count = 0
        await self.start_instance(name)
        state = self.instances.get(name)
        return state is not None and state.status == InstanceStatus.RUNNING

    async def _wait_for_ready(self, state: InstanceState, timeout: float = 90) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not state.process or not state.process.is_alive():
                log.warning(
                    "Instance %s process died during startup",
                    state.config.name,
                )
                return False
            output = state.process.capture(lines=50)
            if KiroBackend.is_ready(output):
                return True
            if output:
                log.debug("Instance %s output: %s", state.config.name, output[-200:])
            await asyncio.sleep(2)
        log.warning("Instance %s timed out waiting for ready", state.config.name)
        return False

    async def _health_loop(self, name: str) -> None:
        state = self.instances[name]
        interval = state.config.restart_policy.health_check_interval_ms / 1000
        while state.status == InstanceStatus.RUNNING:
            await asyncio.sleep(interval)
            if not state.process or not state.process.is_alive():
                state.status = InstanceStatus.CRASHED
                state.crash_count += 1
                log.warning("Instance %s crashed (count=%d)", name, state.crash_count)
                if state.crash_count <= state.config.restart_policy.max_retries:
                    delay = min(2 ** state.crash_count, 60)
                    await asyncio.sleep(delay)
                    await self.start_instance(name)
                return

    async def start_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        sem = asyncio.Semaphore(self.config.startup.concurrency)
        async def _start(name: str) -> None:
            async with sem:
                try:
                    await self.start_instance(name)
                    state = self.instances.get(name)
                    results[name] = state is not None and state.status == InstanceStatus.RUNNING
                except Exception as e:
                    log.error("Failed to start %s: %s", name, e)
                    results[name] = False
        await asyncio.gather(*(_start(n) for n in self.config.instances))
        return results

    async def stop_all(self) -> None:
        await asyncio.gather(*(self.stop_instance(n) for n in list(self.instances)))

    def get_status(self) -> list[dict]:
        return [
            {"name": n, "status": s.status.value, "pid": s.process.pid if s.process else None}
            for n, s in self.instances.items()
        ]

    async def reload_config_and_restart(self) -> dict[str, bool]:
        """Reload team.yaml and restart all instances (including new ones)."""
        from .config import load_team_config
        log.info("Reloading team config...")
        new_config = load_team_config()

        # Stop instances that are no longer in config
        removed = set(self.instances.keys()) - set(new_config.instances.keys())
        for name in removed:
            await self.stop_instance(name)
            self.instances.pop(name, None)

        # Update config
        self.config = new_config

        # Stop all running instances
        await self.stop_all()

        # Start all instances from new config
        results = await self.start_all()
        running = sum(1 for v in results.values() if v)
        log.info("Reload complete: %d/%d running", running, len(results))
        return results
