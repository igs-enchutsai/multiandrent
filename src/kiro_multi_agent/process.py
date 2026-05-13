"""Process management for Kiro CLI instances (asyncio subprocess, Windows-native)."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from dataclasses import dataclass, field

log = logging.getLogger(__name__)


@dataclass
class ManagedProcess:
    """Wraps an asyncio subprocess with stdin/stdout access and output capture."""

    name: str
    proc: asyncio.subprocess.Process | None = None
    _output_lines: list[str] = field(default_factory=list)
    _reader_task: asyncio.Task | None = None
    _max_capture: int = 5000
    _on_output: object = None  # Callable[[str, str], Awaitable[None]] | None
    _pending_response: list[str] = field(default_factory=list)
    _response_event: asyncio.Event | None = None
    _collecting_response: bool = False

    @property
    def pid(self) -> int | None:
        return self.proc.pid if self.proc else None

    def is_alive(self) -> bool:
        return self.proc is not None and self.proc.returncode is None

    async def start(self, cmd: str, cwd: str) -> None:
        full_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
        kwargs = dict(
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
            env=full_env,
        )
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x00000200  # CREATE_NEW_PROCESS_GROUP
        self.proc = await asyncio.create_subprocess_shell(cmd, **kwargs)
        self._output_lines.clear()
        self._reader_task = asyncio.create_task(self._read_output())
        log.info("Process started: %s (pid=%s)", self.name, self.pid)

    async def _read_output(self) -> None:
        assert self.proc and self.proc.stdout
        try:
            buffer = ""
            while True:
                chunk = await self.proc.stdout.read(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")
                # Split on newlines and carriage returns
                while "\n" in buffer or "\r" in buffer:
                    # Find earliest line break
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
                    # Skip empty lines from consecutive \r\n
                    if line:
                        # Strip ANSI escape codes for clean text
                        clean = self._strip_ansi(line)
                        if clean:
                            self._output_lines.append(clean)
                            if len(self._output_lines) > self._max_capture:
                                self._output_lines = self._output_lines[-self._max_capture:]
                            # Notify output callback if set
                            if self._on_output and self._collecting_response:
                                self._pending_response.append(clean)
            # Flush remaining buffer
            if buffer.strip():
                clean = self._strip_ansi(buffer.strip())
                if clean:
                    self._output_lines.append(clean)
                    if self._on_output and self._collecting_response:
                        self._pending_response.append(clean)
        except (asyncio.CancelledError, OSError):
            pass

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape sequences, terminal control codes, and spinner animations."""
        import re
        # Remove ANSI escape sequences (colors, cursor movement, etc.)
        text = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)
        # Remove ANSI escape sequences with ? prefix (cursor show/hide, etc.)
        text = re.sub(r"\x1b\[\?[0-9;]*[a-zA-Z]", "", text)
        # Remove spinner patterns (braille dots + "Thinking...")
        text = re.sub(r"[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]\s*Thinking\.\.\.", "", text)
        # Remove other spinner patterns
        text = re.sub(r"[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]\s*\w+\.\.\.", "", text)
        # Remove remaining braille spinner chars at start of line
        text = re.sub(r"^[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]+\s*", "", text)
        # Clean up multiple spaces
        text = re.sub(r"  +", " ", text)
        return text.strip()

    async def send_input(self, text: str) -> None:
        if not self.proc or not self.proc.stdin:
            raise RuntimeError(f"Process {self.name} has no stdin")
        # Start collecting response
        self._pending_response.clear()
        self._collecting_response = True
        self.proc.stdin.write((text + "\n").encode("utf-8"))
        await self.proc.stdin.drain()

    async def wait_response(self, timeout: float = 900) -> str:
        """Wait for the response to complete.

        Monitors output until kiro-cli prints the time marker (▸ Time:)
        which indicates the response is done. Times out after 15 minutes.
        """
        import logging
        import time
        _log = logging.getLogger(__name__)
        deadline = time.time() + timeout
        last_log = time.time()

        while time.time() < deadline:
            # Check if we see the end-of-response marker
            for line in self._pending_response:
                if "▸ Time:" in line or "Time:" in line:
                    # Response is complete
                    self._collecting_response = False
                    response_lines = self._pending_response.copy()
                    self._pending_response.clear()
                    return self._extract_final_response(response_lines)
            # Log progress every 30 seconds
            if time.time() - last_log > 30:
                _log.info(
                    "[wait] %s: %d lines buffered, last: %s",
                    self.name,
                    len(self._pending_response),
                    self._pending_response[-1][:80] if self._pending_response else "(empty)",
                )
                last_log = time.time()
            await asyncio.sleep(1)

        # Timeout - return whatever we have
        self._collecting_response = False
        response_lines = self._pending_response.copy()
        self._pending_response.clear()

        if response_lines:
            return self._extract_final_response(response_lines)
        return "⏱️ 搜尋超時（超過 15 分鐘），請稍後再試或換個問法。"

    def _extract_final_response(self, response_lines: list[str]) -> str:
        """Extract the final response from kiro-cli output, filtering noise."""

        # Filter out kiro-cli UI noise and extract only the final response
        filtered = []
        skip_patterns = [
            "▸ Time:", "╭─", "╰─", "│", "Model:",
            "Did you know?", "/context", "/model",
            "All tools are now trusted",
            "ask a question",
            "Thinking...",
            "Working...",
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏",
            "[?25", "[?12",
            "Running tool", "using tool:",
            "Completed in", "- Completed",
            "Successfully read", "Reading file:",
            "Reading directory:", "Querying available",
            "I will run the following command:",
            "Purpose:", "max depth:", "max entries:",
            "(from mcp server:",
            "⋮", "with the param",
        ]

        # Find the last ">" prefixed response block
        response_blocks = []
        current_block = []
        in_response = False

        for line in response_lines:
            # Skip UI noise
            if any(skip in line for skip in skip_patterns):
                if in_response and current_block:
                    response_blocks.append("\n".join(current_block))
                    current_block = []
                    in_response = False
                continue

            # Skip JSON-like content (tool parameters)
            stripped = line.strip()
            if stripped in ("{", "}", "[", "]") or stripped.startswith('"') and stripped.endswith('"'):
                continue
            if stripped.startswith('"') and '":' in stripped:
                continue

            # Lines starting with > or following a > line are response content
            if line.startswith("> "):
                in_response = True
                current_block.append(line[2:])  # Remove "> " prefix
            elif line.startswith(">"):
                in_response = True
                current_block.append(line[1:].lstrip())
            elif in_response and line.strip():
                current_block.append(line)
            elif not line.strip():
                if in_response and current_block:
                    current_block.append("")  # Preserve blank lines in response

        if current_block:
            response_blocks.append("\n".join(current_block))

        # Return the last response block (the final answer)
        if response_blocks:
            # Pick the longest block as the final answer
            best = max(response_blocks, key=len)
            return best.strip()

        # Fallback: return all non-noise lines
        for line in response_lines:
            if not any(skip in line for skip in skip_patterns) and line.strip():
                stripped = line.strip()
                if stripped in ("{", "}", "[", "]"):
                    continue
                if stripped.startswith('"') and ('":' in stripped or stripped.endswith('"')):
                    continue
                filtered.append(line)

        return "\n".join(filtered)

    def capture(self, lines: int = 200) -> str:
        return "\n".join(self._output_lines[-lines:])

    async def kill(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
            self._reader_task = None
        if self.proc and self.proc.returncode is None:
            try:
                self.proc.terminate()
                await asyncio.wait_for(self.proc.wait(), timeout=5)
            except (asyncio.TimeoutError, OSError):
                self.proc.kill()
        self.proc = None


# Registry
_active: dict[str, ManagedProcess] = {}

def register(mp: ManagedProcess) -> None:
    _active[mp.name] = mp

def unregister(name: str) -> None:
    _active.pop(name, None)

def list_active() -> list[str]:
    return [name for name, mp in _active.items() if mp.is_alive()]
