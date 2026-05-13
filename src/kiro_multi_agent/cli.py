"""CLI entry point - team start/stop/status/ls/send/init."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from .config import get_home, load_team_config
from .team import TeamManager, run_team


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_team_start(args: argparse.Namespace) -> None:
    try:
        asyncio.run(run_team(args.config))
    except KeyboardInterrupt:
        pass


def cmd_team_stop(args: argparse.Namespace) -> None:
    pid_file = get_home() / "team.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            print("Stop signal sent")
        except (ValueError, ProcessLookupError):
            print("Process not found")


def cmd_team_status(args: argparse.Namespace) -> None:
    config = load_team_config(args.config)
    print(f"Team config: {len(config.instances)} instances defined")
    for name, ic in config.instances.items():
        print(f"  {name:20s} backend={ic.backend:10s} model={ic.model or 'auto'}")


def cmd_init(args: argparse.Namespace) -> None:
    import shutil
    home = get_home()
    home.mkdir(parents=True, exist_ok=True)
    team_yaml = home / "team.yaml"
    if team_yaml.exists() and not args.force:
        print(f"Config already exists: {team_yaml}")
        return
    tpl = Path(__file__).parent / "templates" / "team.yaml"
    if tpl.exists():
        shutil.copy2(tpl, team_yaml)
    else:
        team_yaml.write_text("# kiro-multi-agent team config\ninstances: {}\n")
    print(f"Created: {team_yaml}")
    print("Edit team.yaml, then run: kiro-multi-agent team start")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kiro-multi-agent",
        description="Multi-agent Kiro CLI team manager",
    )
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--log-level", default="INFO")
    sub = parser.add_subparsers(dest="command")

    p_team = sub.add_parser("team", help="Team management")
    team_sub = p_team.add_subparsers(dest="team_cmd")
    team_sub.add_parser("start", help="Start team")
    team_sub.add_parser("stop", help="Stop team")
    team_sub.add_parser("status", help="Show status")

    p_init = sub.add_parser("init", help="Create default team.yaml")
    p_init.add_argument("--force", action="store_true")

    args = parser.parse_args()
    _setup_logging(args.log_level)

    if args.command == "team":
        dispatch = {"start": cmd_team_start, "stop": cmd_team_stop, "status": cmd_team_status}
        fn = dispatch.get(args.team_cmd)
        if fn:
            fn(args)
        else:
            parser.parse_args(["team", "--help"])
    elif args.command == "init":
        cmd_init(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
