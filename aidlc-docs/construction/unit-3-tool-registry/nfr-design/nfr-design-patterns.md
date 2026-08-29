# Unit 3 NFR Design Patterns: Scoped Tool Registry & Built-ins

This document specifies the concrete design patterns implementing workspace path sandboxing (`SECURITY-05`), process tree termination (`RES-02`), and output truncation.

---

## 1. Security Patterns: PathSandbox Component (`SECURITY-05`)

```python
from pathlib import Path

class SecurityAccessError(PermissionError):
    """Raised when a tool attempts to access paths outside the authorized workspace."""
    pass

class PathSandbox:
    """Enforces strict path confinement within workspace_root."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.resolve()

    def resolve_safe_path(self, target_path: str | Path) -> Path:
        """Resolve a path and verify it is strictly within workspace_root."""
        raw_path = Path(target_path)
        if raw_path.is_absolute():
            resolved = raw_path.resolve()
        else:
            resolved = (self.workspace_root / raw_path).resolve()

        if not resolved.is_relative_to(self.workspace_root):
            raise SecurityAccessError(
                f"Access denied: path '{target_path}' is outside workspace root '{self.workspace_root}'"
            )
        return resolved
```

---

## 2. Resilience Patterns: ProcessGroupRunner (`RES-02`)

```python
import os
import signal
import asyncio

class ProcessGroupRunner:
    """Executes subprocesses in dedicated POSIX process groups with complete tree termination."""

    @staticmethod
    async def run_command_with_timeout(
        command: str,
        cwd: Path,
        timeout_seconds: int = 60,
    ) -> tuple[int, str]:
        """Execute command in a process group and terminate the group on timeout."""
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            preexec_fn=os.setsid,  # Create a new process group (POSIX)
        )

        try:
            stdout_bytes, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=float(timeout_seconds),
            )
            output = stdout_bytes.decode("utf-8", errors="replace")
            return proc.returncode or 0, output
        except asyncio.TimeoutError:
            # Send SIGTERM then SIGKILL to process group (RES-02)
            try:
                pgid = os.getpgid(proc.pid)
                os.killpg(pgid, signal.SIGTERM)
                await asyncio.sleep(1.0)
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            raise TimeoutError(f"Command '{command}' timed out after {timeout_seconds}s")
```

---

## 3. Performance Patterns: OutputTruncator

```python
def truncate_output(text: str, max_lines: int = 800, max_bytes: int = 50_000) -> str:
    """Truncate verbose command or file outputs safely."""
    lines = text.splitlines(keepends=True)
    if len(lines) > max_lines:
        truncated_text = "".join(lines[:max_lines])
        return truncated_text + f"\n... [Output truncated: showing first {max_lines} lines]"

    encoded = text.encode("utf-8")
    if len(encoded) > max_bytes:
        truncated_text = encoded[:max_bytes].decode("utf-8", errors="ignore")
        return truncated_text + f"\n... [Output truncated: capped at {max_bytes // 1000}KB]"

    return text
```
