"""Kiro CLI backend - build commands, write MCP config, detect ready state."""
from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

READY_PATTERN = re.compile(
    r"All tools are now trusted|Trust All Tools active|ask a question",
    re.MULTILINE,
)


@dataclass
class KiroBackendConfig:
    working_directory: str = ""
    instance_name: str = ""
    model: str | None = None
    team_api_port: int = 8470
    role: str = "worker"
    allowed_targets: list[str] = field(default_factory=list)


class KiroBackend:
    def __init__(self) -> None:
        # Check multiple possible locations for kiro-cli
        # IMPORTANT: kiro-cli.exe (CLI 2.x) must be preferred over kiro.CMD (IDE launcher)
        candidates = [
            shutil.which("kiro-cli"),
            str(Path.home() / "AppData/Local/Kiro-Cli/kiro-cli.exe"),
            str(Path.home() / "AppData/Local/Programs/Kiro-Cli/LocalApp/Kiro-Cli/kiro-cli.exe"),
            str(Path.home() / "AppData/Local/Programs/Kiro-Cli/kiro-cli.exe"),
            "kiro-cli",
        ]
        self.binary_path = next((c for c in candidates if c and Path(c).exists()), "kiro-cli")

    def build_command(self, cfg: KiroBackendConfig) -> str:
        cmd = f'"{self.binary_path}" chat --trust-all-tools --legacy-ui'
        if cfg.model:
            cmd += f" --model {cfg.model}"
        return cmd

    def write_config(self, cfg: KiroBackendConfig) -> None:
        """Merge team MCP server into existing .kiro/settings/mcp.json."""
        mcp_dir = Path(cfg.working_directory) / ".kiro" / "settings"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        mcp_path = mcp_dir / "mcp.json"

        # Load existing config if present
        existing = {}
        if mcp_path.exists():
            try:
                existing = json.loads(mcp_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = {}

        if "mcpServers" not in existing:
            existing["mcpServers"] = {}

        py_path = shutil.which("py") or shutil.which("python3") or "python"
        # Only update the "team" server entry, preserve others
        existing["mcpServers"]["team"] = {
            "command": py_path,
            "args": [
                "-m", "kiro_multi_agent.team_mcp",
                "--port", str(cfg.team_api_port),
                "--instance", cfg.instance_name,
                "--role", cfg.role,
                "--allowed-targets", ",".join(cfg.allowed_targets),
            ],
        }
        mcp_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    @staticmethod
    def is_ready(output: str) -> bool:
        return bool(READY_PATTERN.search(output))

    @staticmethod
    def quit_command() -> str:
        return "/quit"
