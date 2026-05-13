"""Watchdog: monitor team-agent, auto-restart on crash.

Usage: python scripts/watchdog.py
Checks every 30 seconds, restarts if service is down.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request

TEAM_AGENT_PORT = 8470
CHECK_INTERVAL = 30
MAX_RESTART_PER_HOUR = 5


def is_alive(port: int, path: str = "/api/status") -> bool:
    try:
        url = f"http://127.0.0.1:{port}{path}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_team_agent() -> subprocess.Popen:
    cmd = [sys.executable, "-m", "kiro_multi_agent.cli", "team", "start"]
    print(f"[watchdog] Starting: {' '.join(cmd)}")
    return subprocess.Popen(
        cmd,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> None:
    restart_count = 0
    last_reset = time.time()

    # Load .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    print(f"[watchdog] Started (port={TEAM_AGENT_PORT}, interval={CHECK_INTERVAL}s)")
    proc = start_team_agent()
    time.sleep(15)

    while True:
        try:
            if time.time() - last_reset > 3600:
                restart_count = 0
                last_reset = time.time()

            alive = is_alive(TEAM_AGENT_PORT)
            proc_alive = proc and proc.poll() is None

            if not alive or not proc_alive:
                print(f"[watchdog] Service DOWN (api={alive}, proc={proc_alive})")
                if restart_count >= MAX_RESTART_PER_HOUR:
                    print(f"[watchdog] Max restarts reached, waiting...")
                else:
                    if proc and proc.poll() is None:
                        proc.terminate()
                        proc.wait(timeout=10)
                    time.sleep(3)
                    proc = start_team_agent()
                    restart_count += 1
                    print(f"[watchdog] Restarted (count={restart_count})")
                    time.sleep(15)

            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("[watchdog] Stopping...")
            if proc and proc.poll() is None:
                proc.terminate()
            break
        except Exception as e:
            print(f"[watchdog] Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
