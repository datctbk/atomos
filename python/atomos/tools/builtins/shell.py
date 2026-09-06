"""Built-in shell command execution tool with POSIX process group tree isolation (RES-02)."""

from __future__ import annotations

import asyncio
import os
import signal
import sys
from pathlib import Path

from pydantic import BaseModel, Field

from atomos.guard.sandbox import PathSandbox, SecurityAccessError
from atomos.tools.base import BaseTool, ToolResult


class ProcessGroupRunner:
    """Spawns subprocesses in isolated process groups and terminates entire tree on timeout (RES-02)."""

    @staticmethod
    async def run_command_with_timeout(
        command: str,
        cwd: Path,
        timeout_seconds: int = 60,
    ) -> tuple[int, str]:
        """Execute command in a process group and terminate the group on timeout."""
        # On POSIX systems, spawn in new process group to capture all descendants
        is_posix = sys.platform != "win32"
        preexec = os.setsid if is_posix else None

        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            preexec_fn=preexec,
        )

        try:
            stdout_bytes, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=float(timeout_seconds),
            )
            output = stdout_bytes.decode("utf-8", errors="replace")
            return proc.returncode or 0, output
        except TimeoutError:
            # Process group tree termination (RES-02)
            if is_posix and proc.pid is not None:
                try:
                    pgid = os.getpgid(proc.pid)
                    os.killpg(pgid, signal.SIGTERM)
                    await asyncio.sleep(0.5)
                    os.killpg(pgid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
            else:
                proc.kill()

            raise TimeoutError(f"Command execution timed out after {timeout_seconds} seconds.")


class RunCommandInput(BaseModel):
    """Parameters for run_command tool."""

    command: str = Field(description="Shell command line to execute.")
    cwd: str | None = Field(default=None, description="Working directory relative to workspace root.")
    timeout_seconds: int = Field(default=60, description="Maximum execution duration in seconds.")


class RunCommandTool(BaseTool[RunCommandInput]):
    """Executes a shell command safely within the sandboxed workspace."""

    def __init__(self, sandbox: PathSandbox | None = None) -> None:
        super().__init__(
            name="run_command",
            description="Execute a shell command within the workspace directory with timeout protection.",
            params_model=RunCommandInput,
        )
        self.sandbox = sandbox or PathSandbox()

    async def execute(self, params: RunCommandInput) -> ToolResult:
        target_cwd = params.cwd or "."
        try:
            safe_cwd = self.sandbox.resolve_safe_path(target_cwd)
        except SecurityAccessError as exc:
            return ToolResult(success=False, output="", error=str(exc))

        if not safe_cwd.is_dir():
            return ToolResult(
                success=False,
                output="",
                error=f"NotADirectoryError: Working directory '{safe_cwd}' does not exist.",
            )

        try:
            code, output = await ProcessGroupRunner.run_command_with_timeout(
                command=params.command,
                cwd=safe_cwd,
                timeout_seconds=params.timeout_seconds,
            )
            return ToolResult(
                success=(code == 0),
                output=output,
                error=f"Process exited with status code {code}" if code != 0 else None,
            )
        except TimeoutError as exc:
            return ToolResult(
                success=False,
                output="",
                error=str(exc),
            )
        except OSError as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"SubprocessError: Failed to execute command: {exc}",
            )
