"""Test kiro-cli running as a subprocess with stdin/stdout interaction."""
from __future__ import annotations

import asyncio
import sys
import os

KIRO_CLI = r"C:\Users\jinyiyeh\AppData\Local\Programs\Kiro-Cli\LocalApp\Kiro-Cli\kiro-cli.exe"


async def main() -> None:
    print(f"Starting kiro-cli subprocess...")
    print(f"Binary: {KIRO_CLI}")
    print(f"CWD: {os.getcwd()}")
    print()

    proc = await asyncio.create_subprocess_exec(
        KIRO_CLI, "chat", "--trust-all-tools", "--legacy-ui",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=os.getcwd(),
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )

    print(f"Process started, PID={proc.pid}")
    print("Reading output for 20 seconds...")
    print("=" * 50)

    # Read output for 20 seconds to see startup
    async def read_output():
        assert proc.stdout
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:
                print(f"  > {decoded}")

    try:
        reader_task = asyncio.create_task(read_output())
        await asyncio.sleep(20)

        # Send a test message
        print("=" * 50)
        print("Sending test message: 'say hello in one word'")
        proc.stdin.write(b"say hello in one word\n")
        await proc.stdin.drain()

        # Wait for response
        await asyncio.sleep(15)

        print("=" * 50)
        print("Terminating process...")
        proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=5)
        print("Done!")

    except asyncio.TimeoutError:
        proc.kill()
        print("Force killed")
    except Exception as e:
        print(f"Error: {e}")
        proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
