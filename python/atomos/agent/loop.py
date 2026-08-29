"""Core agent execution loop, sliding window compactor, and multi-turn driver."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from atomos.core.context import Context
from atomos.core.session import Session, SessionEvent, SessionEventType
from atomos.llm.base import (
    BaseLLMAdapter,
    LLMChunk,
    LLMMessage,
    LLMRole,
    ToolCallAccumulator,
    UsageInfo,
)
from atomos.llm.retry import retry_async_stream
from atomos.tools.base import ToolRegistry

logger = logging.getLogger("atomos.agent")


class AgentStatus(str, Enum):
    """Operational status of the agent turn state machine."""

    IDLE = "idle"
    STREAMING = "streaming"
    EXECUTING_TOOLS = "executing_tools"
    COMPACTING = "compacting"
    COMPLETED = "completed"
    ERROR = "error"


class TurnOptions(BaseModel):
    """Configuration options controlling turn execution boundaries."""

    model_config = ConfigDict(frozen=True)

    max_iterations: int = Field(default=25, ge=1, le=100)
    system_prompt: str = ""
    max_history_messages: int = Field(default=50, ge=4)


class ContextCompactor:
    """Maintains message context within budget while preserving system instructions."""

    @staticmethod
    def compact_history(
        events: list[SessionEvent],
        max_messages: int = 50,
        system_prompt: str = "",
    ) -> list[LLMMessage]:
        """Convert session events into chat messages and prune with sliding window."""
        raw_messages: list[LLMMessage] = []
        if system_prompt:
            raw_messages.append(LLMMessage(role=LLMRole.SYSTEM, content=system_prompt))

        for ev in events:
            if ev.type == SessionEventType.USER_MESSAGE:
                raw_messages.append(
                    LLMMessage(role=LLMRole.USER, content=ev.payload.get("text", ""))
                )
            elif ev.type == SessionEventType.ASSISTANT_MESSAGE:
                raw_messages.append(
                    LLMMessage(
                        role=LLMRole.ASSISTANT,
                        content=ev.payload.get("text", ""),
                        tool_calls=ev.payload.get("tool_calls"),
                    )
                )
            elif ev.type == SessionEventType.TOOL_RESULT:
                output_str = ev.payload.get("result", {}).get("output") or ""
                error_str = ev.payload.get("result", {}).get("error") or ""
                body = output_str if output_str else f"Error: {error_str}"
                raw_messages.append(
                    LLMMessage(
                        role=LLMRole.TOOL,
                        name=ev.payload.get("name"),
                        tool_call_id=ev.payload.get("tool_call_id"),
                        content=body,
                    )
                )

        if len(raw_messages) <= max_messages:
            return raw_messages

        # Sliding window: keep system prompt (index 0) + last (max_messages - 1)
        has_system = raw_messages and raw_messages[0].role == LLMRole.SYSTEM
        system_msg = raw_messages[0] if has_system else None
        non_system = [m for m in raw_messages if m.role != LLMRole.SYSTEM]
        keep_count = max_messages - 1 if has_system else max_messages
        trimmed = non_system[-keep_count:] if keep_count > 0 else []

        return ([system_msg] if system_msg else []) + trimmed


class AgentLoop:
    """Orchestrates streaming LLM turns, tool invocations, and session event sourcing."""

    def __init__(
        self,
        context: Context,
        session: Session,
        llm_adapter: BaseLLMAdapter,
        tool_registry: ToolRegistry,
    ) -> None:
        self.context = context
        self.session = session
        self.llm_adapter = llm_adapter
        self.tool_registry = tool_registry
        self.status = AgentStatus.IDLE
        self.cumulative_usage = UsageInfo()

    async def run_turn(
        self,
        user_prompt: str,
        options: TurnOptions | None = None,
    ) -> AsyncIterator[str]:
        """Execute a full agent turn, yielding token strings in real time."""
        opts = options or TurnOptions()
        self.status = AgentStatus.STREAMING

        # 1. Persist User Message
        self.session.append_event(SessionEventType.USER_MESSAGE, {"text": user_prompt})
        await self.context.emit(
            "agent/turn_start",
            {"session_id": self.session.session_id, "prompt": user_prompt},
        )

        iteration = 0
        try:
            while iteration < opts.max_iterations:
                iteration += 1
                messages = ContextCompactor.compact_history(
                    self.session.events,
                    max_messages=opts.max_history_messages,
                    system_prompt=opts.system_prompt,
                )
                tools = self.tool_registry.get_openai_tools()
                accumulator = ToolCallAccumulator()
                full_text = ""
                final_usage: UsageInfo | None = None

                # Stream tokens from adapter wrapped with full jitter retry
                def _make_stream_factory(
                    msgs: list[LLMMessage],
                    tls: list[dict[str, Any]] | None,
                ) -> Any:
                    async def _factory() -> AsyncIterator[LLMChunk]:
                        async for chunk in self.llm_adapter.stream(msgs, tls):
                            yield chunk
                    return _factory

                active_tools = tools if tools else None
                async for chunk in retry_async_stream(_make_stream_factory(messages, active_tools)):
                    if chunk.delta_content:
                        full_text += chunk.delta_content
                        await self.context.emit("agent/token", {"delta": chunk.delta_content})
                        yield chunk.delta_content

                    for frag in chunk.delta_tool_calls:
                        accumulator.add_fragment(frag)

                    if chunk.usage:
                        final_usage = chunk.usage

                if final_usage:
                    self.cumulative_usage = UsageInfo(
                        prompt_tokens=self.cumulative_usage.prompt_tokens + final_usage.prompt_tokens,
                        completion_tokens=self.cumulative_usage.completion_tokens + final_usage.completion_tokens,
                        total_tokens=self.cumulative_usage.total_tokens + final_usage.total_tokens,
                    )

                tool_calls = accumulator.get_tool_calls()
                # 2. Persist Assistant Message
                self.session.append_event(
                    SessionEventType.ASSISTANT_MESSAGE,
                    {
                        "text": full_text,
                        "tool_calls": tool_calls if tool_calls else None,
                        "usage": final_usage.model_dump() if final_usage else None,
                    },
                )

                if not tool_calls:
                    # Completed without requesting tools
                    break

                # 3. Execute requested tools sequentially
                self.status = AgentStatus.EXECUTING_TOOLS
                for tc in tool_calls:
                    call_id = tc["id"]
                    func = tc["function"]
                    func_name = func["name"]
                    func_args = func["arguments"]

                    await self.context.emit(
                        "agent/tool_start",
                        {"id": call_id, "name": func_name, "args": func_args},
                    )

                    res = await self.tool_registry.execute_tool(func_name, func_args)

                    self.session.append_event(
                        SessionEventType.TOOL_RESULT,
                        {"tool_call_id": call_id, "name": func_name, "result": res.to_dict()},
                    )

                    await self.context.emit(
                        "agent/tool_end",
                        {"id": call_id, "result": res.to_dict()},
                    )

                self.status = AgentStatus.STREAMING

            if iteration >= opts.max_iterations and tool_calls:
                warning_msg = (
                    f"\n[Warning: Reached maximum turn iterations limit ({opts.max_iterations})]"
                )
                yield warning_msg

            self.status = AgentStatus.COMPLETED

        except asyncio.CancelledError:
            self.status = AgentStatus.ERROR
            self.session.append_event(
                SessionEventType.AGENT_INTERRUPT,
                {"reason": "Turn cancelled by caller or user interrupt"},
            )
            await self.context.emit(
                "agent/turn_cancelled",
                {"session_id": self.session.session_id},
            )
            raise
        except Exception as exc:
            self.status = AgentStatus.ERROR
            logger.exception("Uncaught error during agent turn")
            self.session.append_event(
                SessionEventType.AGENT_INTERRUPT,
                {"reason": f"Unhandled exception: {exc}"},
            )
            raise
        finally:
            await self.context.emit(
                "agent/turn_end",
                {
                    "session_id": self.session.session_id,
                    "iterations": iteration,
                    "cumulative_usage": self.cumulative_usage.model_dump(),
                },
            )
