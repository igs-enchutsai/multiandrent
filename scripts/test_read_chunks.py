"""Test reading kiro-cli output using chunk-based read (same as process.py)."""
from __future__ import annotations

import asyncio
import os
import re

KIRO_CLI = r"C:\Users\jinyiyeh\AppData\Local\Programs\Kiro-Cli\LocalApp\Kiro-Cli\kiro-cli.exe"
READY_PATTERN = re.compile(
    r"All tools are now trusted|Trust All Tools active|ask a question",
    re.MULTILINE,
)


async def main():
    cwd = os.path.abspath("./agents/leader-agent")
    cmd = f'"{KIRO_CLI}" chat --trust-all-tools --legacy-ui'

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )
    print(f"PID: {proc.pid}, reading chunks for 25s...")

    lines = []
    buffer = ""

    async def read_chunks():
        nonlocal buffer
        while True:
            chunk = await proc.stdout.read(4096)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            while "\n" in buffer or "\r" in buffer:
                nl = buffer.find("\n")
                cr = buffer.find("\r")
                if nl == -1:
                    pos = cr
                elif cr == -1:
                    pos = nl
                else:
                    pos = min(nl, cr)
                line = buffer[:pos].rstrip()
                buffer = buffer[pos + 1:]
                if line:
                    lines.append(line)

    task = asyncio.create_task(read_chunks())
    await asyncio.sleep(25)

    print(f"\nCaptured {len(lines)} lines:")
    for i, line in enumerate(lines[-30:]):
        clean = line.replace("\x1b", "\\x1b")[:120]
        print(f"  [{i}] {clean}")

    # Check ready pattern
    full_output = "\n".join(lines)
    if READY_PATTERN.search(full_output):
        print("\n*** READY PATTERN FOUND! ***")
    else:
        print("\n*** READY PATTERN NOT FOUND ***")
        print(f"Total output length: {len(full_output)} chars")

    proc.terminate()
    task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
