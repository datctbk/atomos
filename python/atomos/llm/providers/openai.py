"""OpenAI & Local LLM (Ollama, LMStudio, vLLM) streaming adapter."""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from typing import Any

import httpx

from atomos.llm.base import (
    BaseLLMAdapter,
    LLMChunk,
    LLMMessage,
    ToolCallFragment,
    UsageInfo,
)


class OpenAIAdapter(BaseLLMAdapter):
    """Streaming adapter for OpenAI and OpenAI-compatible local runtimes (Ollama, LMStudio, vLLM)."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
        is_local: bool = False,
    ) -> None:
        self.is_local = is_local
        if is_local:
            # Default to local Ollama / LMStudio endpoint without requiring API keys
            resolved_base_url = base_url or os.environ.get(
                "ATOMOS_LOCAL_LLM_URL", "http://localhost:11434/v1"
            )
            resolved_api_key = api_key or "local-no-key"
        else:
            resolved_base_url = base_url or "https://api.openai.com/v1"
            resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

        super().__init__(
            model=model,
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMChunk]:
        """Stream SSE chunks from OpenAI or local OpenAI-compatible endpoint."""
        base = (self.base_url or "https://api.openai.com/v1").rstrip("/")
        url = f"{base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [m.model_dump(exclude_none=True) for m in messages],
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        timeout = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
        async with (
            httpx.AsyncClient(timeout=timeout) as client,
            client.stream("POST", url, headers=headers, json=payload) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                    clean_line = line.strip()
                    if not clean_line or not clean_line.startswith("data:"):
                        continue
                    data_str = clean_line[len("data:") :].strip()
                    if data_str == "[DONE]":
                        break

                    try:
                        chunk_json = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk_json.get("choices", [])
                    if not choices:
                        continue

                    choice = choices[0]
                    delta = choice.get("delta", {})
                    finish_reason = choice.get("finish_reason")

                    delta_content = delta.get("content") or ""
                    delta_tools: list[ToolCallFragment] = []

                    raw_tool_calls = delta.get("tool_calls", [])
                    for tc in raw_tool_calls:
                        idx = tc.get("index", 0)
                        tc_id = tc.get("id")
                        func = tc.get("function", {})
                        func_name = func.get("name")
                        func_args = func.get("arguments") or ""
                        delta_tools.append(
                            ToolCallFragment(
                                index=idx,
                                id=tc_id,
                                name=func_name,
                                arguments=func_args,
                            )
                        )

                    usage_obj = None
                    if chunk_json.get("usage"):
                        u = chunk_json["usage"]
                        usage_obj = UsageInfo(
                            prompt_tokens=u.get("prompt_tokens", 0),
                            completion_tokens=u.get("completion_tokens", 0),
                            total_tokens=u.get("total_tokens", 0),
                        )

                    yield LLMChunk(
                        delta_content=delta_content,
                        delta_tool_calls=delta_tools,
                        finish_reason=finish_reason,
                        usage=usage_obj,
                    )
