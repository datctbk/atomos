"""Base models, tool abstractions, execution result schemas, and scoped tool registry."""

from __future__ import annotations

import abc
import json
import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from atomos.core.context import Disposable

TParams = TypeVar("TParams", bound=BaseModel)
logger = logging.getLogger("atomos.tools")


def truncate_output(text: str, max_lines: int = 800, max_bytes: int = 50_000) -> str:
    """Truncate tool output if exceeding line or byte limits to protect LLM context windows."""
    lines = text.splitlines(keepends=True)
    if len(lines) > max_lines:
        truncated = "".join(lines[:max_lines])
        return truncated + f"\n... [Output truncated: showing first {max_lines} lines]"

    encoded = text.encode("utf-8")
    if len(encoded) > max_bytes:
        truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
        return truncated + f"\n... [Output truncated: capped at {max_bytes // 1000}KB]"

    return text


class ToolResult(BaseModel):
    """Execution output representation returned from tool invocations."""

    model_config = ConfigDict(frozen=True)

    success: bool
    output: str = ""
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for session event persistence or prompt context injection."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseTool(abc.ABC, Generic[TParams]):
    """Abstract generic tool with automatic OpenAI JSON schema generation."""

    def __init__(
        self,
        name: str,
        description: str,
        params_model: type[TParams],
    ) -> None:
        self.name = name
        self.description = description
        self.params_model = params_model

    def to_openai_tool(self) -> dict[str, Any]:
        """Generate OpenAI-compatible tool definition directly from Pydantic schema."""
        raw_schema = self.params_model.model_json_schema()
        # Clean up Pydantic metadata
        raw_schema.pop("title", None)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": raw_schema,
            },
        }

    @abc.abstractmethod
    async def execute(self, params: TParams) -> ToolResult:
        """Strongly-typed execution handler implemented by concrete tools."""
        ...


class ToolRegistry:
    """Scoped registry managing available tools and dispatching validated invocations."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool[Any]] = {}

    def register_tool(self, tool: BaseTool[Any]) -> Disposable:
        """Register a tool and return a Disposable unbinding handle."""
        self._tools[tool.name] = tool

        class _ToolDisposable(Disposable):
            def __init__(self, registry: ToolRegistry, tool_name: str) -> None:
                self._registry = registry
                self._name = tool_name

            def dispose(self) -> None:
                self._registry._tools.pop(self._name, None)

        return _ToolDisposable(self, tool.name)

    def get_tool(self, name: str) -> BaseTool[Any] | None:
        """Retrieve tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool[Any]]:
        """Return all registered tools."""
        return list(self._tools.values())

    def get_openai_tools(self) -> list[dict[str, Any]]:
        """Export all registered tools as OpenAI-compatible schema array."""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute_tool(self, name: str, raw_json_args: str | dict[str, Any]) -> ToolResult:
        """Safely parse arguments, validate parameters, and execute tool (SECURITY-08)."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"ToolNotFoundError: Tool '{name}' is not registered in registry.",
            )

        # Parse JSON string if necessary
        parsed_dict: dict[str, Any]
        if isinstance(raw_json_args, str):
            clean_str = raw_json_args.strip()
            if not clean_str:
                parsed_dict = {}
            else:
                try:
                    parsed_dict = json.loads(clean_str)
                except json.JSONDecodeError as exc:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"JSONDecodeError: Failed to parse tool arguments: {exc}",
                    )
        else:
            parsed_dict = raw_json_args

        # Validate against tool's Pydantic model
        try:
            params = tool.params_model.model_validate(parsed_dict)
        except ValidationError as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"ValidationError: Invalid parameters for '{name}': {exc.errors()}",
            )

        # Execute with exception boundary
        try:
            result = await tool.execute(params)
            # Ensure output is context-safe
            truncated = truncate_output(result.output)
            return ToolResult(
                success=result.success,
                output=truncated,
                error=result.error,
            )
        except Exception as exc:
            logger.exception("Unhandled exception executing tool %s", name)
            return ToolResult(
                success=False,
                output="",
                error=f"{type(exc).__name__}: {exc}",
            )
