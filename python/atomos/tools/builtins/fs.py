"""Built-in filesystem tools with strict workspace sandboxing (SECURITY-05)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from atomos.tools.base import BaseTool, ToolResult


class SecurityAccessError(PermissionError):
    """Raised when an operation attempts to access paths outside the sandbox."""



class PathSandbox:
    """Enforces strict path confinement within workspace_root."""

    def __init__(self, workspace_root: Path | str | None = None) -> None:
        raw = Path(workspace_root) if workspace_root else Path.cwd()
        self.workspace_root = raw.expanduser().resolve()

    def resolve_safe_path(self, target_path: str | Path) -> Path:
        """Resolve a path and verify it resides strictly inside workspace_root."""
        raw_path = Path(target_path).expanduser()
        if raw_path.is_absolute():
            resolved = raw_path.resolve()
        else:
            resolved = (self.workspace_root / raw_path).resolve()

        if not resolved.is_relative_to(self.workspace_root):
            raise SecurityAccessError(
                f"SecurityAccessError: Path '{target_path}' resolves to '{resolved}', "
                f"which is outside authorized workspace root '{self.workspace_root}'."
            )
        return resolved


# 1. ViewFileTool
class ViewFileInput(BaseModel):
    """Parameters for view_file tool."""

    file_path: str = Field(description="Relative or absolute path of the file to view.")
    offset: int = Field(default=1, description="1-indexed line offset to start reading from.")
    limit: int = Field(default=800, description="Maximum number of lines to read.")


class ViewFileTool(BaseTool[ViewFileInput]):
    """Reads lines from a file within the sandboxed workspace."""

    def __init__(self, sandbox: PathSandbox | None = None) -> None:
        super().__init__(
            name="view_file",
            description="View the contents of a file within the workspace with line numbers and slicing.",
            params_model=ViewFileInput,
        )
        self.sandbox = sandbox or PathSandbox()

    async def execute(self, params: ViewFileInput) -> ToolResult:
        try:
            safe_path = self.sandbox.resolve_safe_path(params.file_path)
        except SecurityAccessError as exc:
            return ToolResult(success=False, output="", error=str(exc))

        if not safe_path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"FileNotFoundError: File '{params.file_path}' does not exist.",
            )
        if safe_path.is_dir():
            return ToolResult(
                success=False,
                output="",
                error=f"IsADirectoryError: Path '{params.file_path}' is a directory, not a file.",
            )

        try:
            text = safe_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"IOError: Failed to read file '{params.file_path}': {exc}",
            )

        lines = text.splitlines()
        start_idx = max(0, params.offset - 1)
        end_idx = min(len(lines), start_idx + params.limit)
        sliced_lines = lines[start_idx:end_idx]

        numbered_lines = [
            f"{start_idx + idx + 1:4d}: {line}" for idx, line in enumerate(sliced_lines)
        ]
        body = "\n".join(numbered_lines)
        header = f"=== File: {params.file_path} (Lines {start_idx + 1} to {end_idx} of {len(lines)}) ===\n"

        return ToolResult(
            success=True,
            output=header + body,
            error=None,
        )


# 2. WriteFileTool
class WriteFileInput(BaseModel):
    """Parameters for write_to_file tool."""

    file_path: str = Field(description="Relative or absolute path of the file to create or overwrite.")
    content: str = Field(description="Complete text content to write into the file.")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing files.")


class WriteFileTool(BaseTool[WriteFileInput]):
    """Creates or overwrites a file safely within the sandboxed workspace."""

    def __init__(self, sandbox: PathSandbox | None = None) -> None:
        super().__init__(
            name="write_to_file",
            description="Create a new file or overwrite an existing file with the specified content.",
            params_model=WriteFileInput,
        )
        self.sandbox = sandbox or PathSandbox()

    async def execute(self, params: WriteFileInput) -> ToolResult:
        try:
            safe_path = self.sandbox.resolve_safe_path(params.file_path)
        except SecurityAccessError as exc:
            return ToolResult(success=False, output="", error=str(exc))

        if safe_path.exists() and not params.overwrite:
            return ToolResult(
                success=False,
                output="",
                error=f"FileExistsError: File '{params.file_path}' already exists. Set overwrite=True to replace.",
            )

        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(params.content, encoding="utf-8")
            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(params.content)} characters to '{params.file_path}'.",
                error=None,
            )
        except OSError as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"IOError: Failed to write to file '{params.file_path}': {exc}",
            )


# 3. ReplaceFileTool
class ReplaceFileInput(BaseModel):
    """Parameters for replace_file_content tool."""

    file_path: str = Field(description="Relative or absolute path of the file to modify.")
    old_string: str = Field(description="Exact substring to find and replace.")
    new_string: str = Field(description="Replacement string.")
    replace_all: bool = Field(default=False, description="Whether to replace all occurrences or expect exactly one.")


class ReplaceFileTool(BaseTool[ReplaceFileInput]):
    """Performs exact text replacements in a file within the sandboxed workspace."""

    def __init__(self, sandbox: PathSandbox | None = None) -> None:
        super().__init__(
            name="replace_file_content",
            description="Replace exact text substring occurrences inside a file.",
            params_model=ReplaceFileInput,
        )
        self.sandbox = sandbox or PathSandbox()

    async def execute(self, params: ReplaceFileInput) -> ToolResult:
        try:
            safe_path = self.sandbox.resolve_safe_path(params.file_path)
        except SecurityAccessError as exc:
            return ToolResult(success=False, output="", error=str(exc))

        if not safe_path.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"FileNotFoundError: File '{params.file_path}' does not exist.",
            )

        try:
            content = safe_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"IOError: Failed to read file '{params.file_path}': {exc}",
            )

        occurrences = content.count(params.old_string)
        if occurrences == 0:
            return ToolResult(
                success=False,
                output="",
                error=f"ValueError: Target 'old_string' not found in '{params.file_path}'.",
            )

        if occurrences > 1 and not params.replace_all:
            return ToolResult(
                success=False,
                output="",
                error=f"AmbiguityError: Found {occurrences} occurrences of 'old_string'. "
                f"Set replace_all=True or specify a more unique target string.",
            )

        new_content = content.replace(params.old_string, params.new_string)
        try:
            safe_path.write_text(new_content, encoding="utf-8")
            return ToolResult(
                success=True,
                output=f"Successfully replaced {occurrences} occurrence(s) in '{params.file_path}'.",
                error=None,
            )
        except OSError as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"IOError: Failed to save changes to '{params.file_path}': {exc}",
            )
