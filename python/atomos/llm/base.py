"""Base types, message structures, streaming chunks, and abstract LLM adapter."""

from __future__ import annotations

import abc
from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LLMRole(str, Enum):
    """Role classification for LLM messages."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class LLMMessage(BaseModel):
    """Unified chat message representation."""

    model_config = ConfigDict(extra="ignore")

    role: LLMRole
    content: str = ""
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ToolCallFragment(BaseModel):
    """Incremental delta fragment for streaming tool calls."""

    model_config = ConfigDict(frozen=True)

    index: int = 0
    id: str | None = None
    name: str | None = None
    arguments: str = ""


class UsageInfo(BaseModel):
    """Token consumption accounting."""

    model_config = ConfigDict(frozen=True)

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMChunk(BaseModel):
    """Streaming chunk delta yielded by LLM adapters."""

    model_config = ConfigDict(frozen=True)

    delta_content: str = ""
    delta_reasoning: str = ""
    delta_tool_calls: list[ToolCallFragment] = Field(default_factory=list)
    finish_reason: str | None = None
    usage: UsageInfo | None = None


class ToolCallAccumulator:
    """Accumulates fragmented streaming tool calls into complete tool dictionaries."""

    def __init__(self) -> None:
        self._calls: dict[int, dict[str, Any]] = {}

    def add_fragment(self, fragment: ToolCallFragment) -> None:
        """Merge an incoming tool call fragment by index."""
        idx = fragment.index
        if idx not in self._calls:
            self._calls[idx] = {
                "id": fragment.id or "",
                "type": "function",
                "name": fragment.name or "",
                "arguments": fragment.arguments,
            }
        else:
            entry = self._calls[idx]
            if fragment.id:
                entry["id"] = fragment.id
            if fragment.name:
                entry["name"] = fragment.name
            entry["arguments"] += fragment.arguments

    def get_tool_calls(self) -> list[dict[str, Any]]:
        """Return the sorted list of reconstructed tool calls."""
        sorted_indices = sorted(self._calls.keys())
        result: list[dict[str, Any]] = []
        for idx in sorted_indices:
            c = self._calls[idx]
            result.append(
                {
                    "id": c["id"],
                    "type": "function",
                    "function": {
                        "name": c["name"],
                        "arguments": c["arguments"],
                    },
                }
            )
        return result

    def clear(self) -> None:
        """Reset accumulated tool calls."""
        self._calls.clear()


class BaseLLMAdapter(abc.ABC):
    """Abstract base class for all LLM provider adapters."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    @abc.abstractmethod
    def stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMChunk]:
        """Asynchronously yield token chunks and tool call fragments."""
        ...
