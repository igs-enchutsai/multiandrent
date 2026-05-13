"""team.yaml configuration loading and validation."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_HOME = Path.home() / ".kiro-multi-agent"


def get_home() -> Path:
    if env := os.environ.get("KIRO_MULTI_AGENT_HOME"):
        return Path(env)
    cwd = Path.cwd()
    for p in [cwd, *cwd.parents]:
        if (p / "team.yaml").exists():
            return p
    return DEFAULT_HOME


def get_state_dir() -> Path:
    d = get_home() / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


@dataclass
class CostGuardConfig:
    daily_limit_usd: float = 0
    warn_at_percentage: int = 80
    timezone: str = "UTC"


@dataclass
class HangDetectorConfig:
    enabled: bool = True
    timeout_minutes: int = 60


@dataclass
class StartupConfig:
    concurrency: int = 3
    stagger_delay_ms: int = 2000


@dataclass
class RestartPolicy:
    max_retries: int = 10
    backoff: str = "exponential"
    reset_after: int = 300
    health_check_interval_ms: int = 30000


@dataclass
class InstanceConfig:
    name: str = ""
    working_directory: str = ""
    description: str = ""
    topic_id: int | None = None
    general_topic: bool = False
    role: str = "worker"
    backend: str = "kiro-cli"
    model: str | None = None
    restart_policy: RestartPolicy = field(default_factory=RestartPolicy)


@dataclass
class ChannelConfig:
    bot_token_env: str = "TELEGRAM_BOT_TOKEN"
    group_id: int = 0
    general_topic_id: int = 1


@dataclass
class AccessConfig:
    mode: str = "locked"
    allowed_users: list[int] = field(default_factory=list)


@dataclass
class TeamConfig:
    instances: dict[str, InstanceConfig] = field(default_factory=dict)
    defaults: dict = field(default_factory=dict)
    startup: StartupConfig = field(default_factory=StartupConfig)
    cost_guard: CostGuardConfig = field(default_factory=CostGuardConfig)
    hang_detector: HangDetectorConfig = field(default_factory=HangDetectorConfig)
    channel: ChannelConfig = field(default_factory=ChannelConfig)
    access: AccessConfig = field(default_factory=AccessConfig)
    health_port: int = 8470


def load_team_config(path: Path | None = None) -> TeamConfig:
    if path is None:
        path = get_home() / "team.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Team config not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    defaults = raw.get("defaults", {})
    fc = TeamConfig()

    if "cost_guard" in raw:
        fc.cost_guard = CostGuardConfig(**raw["cost_guard"])
    if "hang_detector" in raw:
        fc.hang_detector = HangDetectorConfig(**raw["hang_detector"])

    fc.health_port = raw.get("health_port", 8470)

    ch = raw.get("channel", {})
    if ch:
        fc.channel = ChannelConfig(**{k: v for k, v in ch.items() if hasattr(ChannelConfig, k)})

    ac = raw.get("access", {})
    if ac:
        fc.access = AccessConfig(**{k: v for k, v in ac.items() if hasattr(AccessConfig, k)})

    for name, inst_raw in raw.get("instances", {}).items():
        merged = {**defaults, **(inst_raw or {})}
        ic = InstanceConfig(name=name)
        for k, v in merged.items():
            if hasattr(ic, k):
                setattr(ic, k, v)
        if not ic.working_directory:
            ic.working_directory = str(get_home() / name)
        fc.instances[name] = ic

    return fc
