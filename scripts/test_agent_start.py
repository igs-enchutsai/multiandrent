"""Debug: test starting kiro-cli from agent working directory."""
from __future__ import annotations

import asyncio
import os


KIRO_CLI = r"C:\Users\jinyiyeh\AppData\Local\Programs\Kiro-Cli\LocalApp\Kiro-Cli\kiro-cli.exe"


async def test():
    cwd = os.path.abspath("./agents/leader-agent")
    print(f"CWD: {cwd}")
    print(f"Exists: {os.path.isdir(cwd)}")

    cmd = f'"{KIRO_CLI}" chat --trust-all-tools --legacy-ui'
    print(f"CMD: {cmd}")

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd,
        env={**os.environ, "PYTHONUTF8": "1"},
    )
    print(f"PID: {proc.pid}")

    # Read output for 10 seconds
    lines = []
    try:
        for _ in range(50):
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=0.5)
            if not line:
                break
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded.strip():
                lines.append(decoded)
                print(f"  > {decoded}")
    except asyncio.TimeoutError:
        pass

    await asyncio.sleep(5)
    alive = proc.returncode is None
    print(f"\nAlive after 5s: {alive}")
    if not alive:
        print(f"Exit code: {proc.returncode}")

    proc.terminate()
    try:
        await asyncio.wait_for(proc.wait(), timeout=5)
    except asyncio.TimeoutError:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(test())
