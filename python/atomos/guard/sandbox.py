"""Filesystem path boundary sandboxing and path traversal defenses (SECURITY-05)."""

from __future__ import annotations

from pathlib import Path


class SecurityAccessError(PermissionError):
    """Raised when an operation attempts to breach the workspace boundary."""


class PathSandbox:
    """Enforces that all file interactions remain strictly within the workspace root."""

    def __init__(self, workspace_root: Path | str | None = None) -> None:
        self.workspace_root = Path(workspace_root or Path.cwd()).resolve()

    def resolve_safe_path(self, relative_or_absolute: str | Path) -> Path:
        """Resolve a path and ensure it strictly resides within the sandboxed root."""
        raw_path = Path(relative_or_absolute)
        if not raw_path.is_absolute():
            resolved = (self.workspace_root / raw_path).resolve()
        else:
            resolved = raw_path.resolve()

        # Check if the resolved path is within workspace_root
        if not resolved.is_relative_to(self.workspace_root):
            raise SecurityAccessError(
                f"SecurityAccessError: Path '{relative_or_absolute}' resolves to '{resolved}', "
                f"which is outside authorized workspace root '{self.workspace_root}'."
            )

        return resolved
