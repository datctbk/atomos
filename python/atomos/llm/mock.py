"""Deterministic mock LLM adapter for offline unit and integration tests."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from atomos.llm.base import (
    BaseLLMAdapter,
    LLMChunk,
    LLMMessage,
    UsageInfo,
)


class MockLLMAdapter(BaseLLMAdapter):
    """Yields pre-canned token chunks or simulated tool calls deterministically."""

    def __init__(
        self,
        canned_chunks: list[LLMChunk] | None = None,
        canned_text: str | None = None,
        simulated_delay: float = 0.0,
    ) -> None:
        super().__init__(model="mock-model")
        self.canned_chunks = canned_chunks
        self.canned_text = canned_text
        self.simulated_delay = simulated_delay

    async def stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMChunk]:
        """Yield canned chunks or words incrementally."""
        if self.canned_chunks is not None:
            for chunk in self.canned_chunks:
                if self.simulated_delay > 0:
                    await asyncio.sleep(self.simulated_delay)
                yield chunk
            return

        text = self.canned_text or "This is a canned response from the mock adapter."
        words = text.split(" ")
        for idx, word in enumerate(words):
            if self.simulated_delay > 0:
                await asyncio.sleep(self.simulated_delay)
            token = word if idx == 0 else " " + word
            is_last = idx == len(words) - 1
            yield LLMChunk(
                delta_content=token,
                delta_tool_calls=[],
                finish_reason="stop" if is_last else None,
                usage=UsageInfo(prompt_tokens=10, completion_tokens=len(words), total_tokens=10 + len(words))
                if is_last
                else None,
            )
