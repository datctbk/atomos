from pathlib import Path
from typing import Any

import pytest

from atomos.agent.loop import AgentLoop, AgentStatus, TurnOptions
from atomos.core.context import Context
from atomos.core.session import SessionEventType, SessionStore
from atomos.llm.base import LLMChunk, ToolCallFragment, UsageInfo
from atomos.llm.mock import MockLLMAdapter
from atomos.tools.base import ToolRegistry
from atomos.tools.builtins.fs import PathSandbox, ViewFileTool, WriteFileTool


@pytest.mark.asyncio
async def test_agent_loop_simple_turn_streaming(tmp_path: Path) -> None:
    ctx = Context()
    store = SessionStore(base_dir=tmp_path)
    session = store.create_session("sess_turn_1")
    adapter = MockLLMAdapter(canned_text="Hello world from Atomos agent")
    registry = ToolRegistry()

    loop = AgentLoop(context=ctx, session=session, llm_adapter=adapter, tool_registry=registry)

    tokens = []
    async for tok in loop.run_turn("Hi"):
        tokens.append(tok)

    assert "".join(tokens) == "Hello world from Atomos agent"
    assert loop.status == AgentStatus.COMPLETED
    assert len(session.events) == 2
    assert session.events[0].type == SessionEventType.USER_MESSAGE
    assert session.events[1].type == SessionEventType.ASSISTANT_MESSAGE


@pytest.mark.asyncio
async def test_agent_loop_tool_execution_turn(tmp_path: Path) -> None:
    ctx = Context()
    store = SessionStore(base_dir=tmp_path)
    session = store.create_session("sess_turn_2")
    sandbox = PathSandbox(workspace_root=tmp_path)
    registry = ToolRegistry()
    registry.register_tool(WriteFileTool(sandbox=sandbox))
    registry.register_tool(ViewFileTool(sandbox=sandbox))

    # Step 1: LLM yields tool call chunk
    tool_chunk = LLMChunk(
        delta_content="",
        delta_tool_calls=[
            ToolCallFragment(
                index=0,
                id="call_write_1",
                name="write_to_file",
                arguments='{"file_path": "agent_out.txt", "content": "Tool executed by Agent"}',
            )
        ],
        finish_reason="tool_calls",
        usage=UsageInfo(prompt_tokens=15, completion_tokens=10, total_tokens=25),
    )
    # Step 2: Final response
    final_chunk = LLMChunk(
        delta_content="I have written the file successfully.",
        delta_tool_calls=[],
        finish_reason="stop",
        usage=UsageInfo(prompt_tokens=30, completion_tokens=10, total_tokens=40),
    )

    class MultiStepMockAdapter(MockLLMAdapter):
        def __init__(self) -> None:
            super().__init__()
            self.step = 0

        async def stream(
            self,
            messages: list[Any],
            tools: list[dict[str, Any]] | None = None,
        ) -> Any:
            self.step += 1
            if self.step == 1:
                yield tool_chunk
            else:
                yield final_chunk

    adapter = MultiStepMockAdapter()
    loop = AgentLoop(context=ctx, session=session, llm_adapter=adapter, tool_registry=registry)

    tokens = []
    async for tok in loop.run_turn("Please write agent_out.txt"):
        tokens.append(tok)

    assert "".join(tokens) == "I have written the file successfully."
    assert (tmp_path / "agent_out.txt").read_text() == "Tool executed by Agent"
    assert len(session.events) == 4
    assert session.events[0].type == SessionEventType.USER_MESSAGE
    assert session.events[1].type == SessionEventType.ASSISTANT_MESSAGE
    assert session.events[2].type == SessionEventType.TOOL_RESULT
    assert session.events[3].type == SessionEventType.ASSISTANT_MESSAGE
    assert loop.cumulative_usage.total_tokens == 65


@pytest.mark.asyncio
async def test_agent_loop_max_iterations_guardrail(tmp_path: Path) -> None:
    ctx = Context()
    store = SessionStore(base_dir=tmp_path)
    session = store.create_session("sess_turn_3")
    sandbox = PathSandbox(workspace_root=tmp_path)
    registry = ToolRegistry()
    registry.register_tool(WriteFileTool(sandbox=sandbox))

    # Infinite tool calling loop simulator
    infinite_tool_chunk = LLMChunk(
        delta_content="",
        delta_tool_calls=[
            ToolCallFragment(
                index=0,
                id="call_inf",
                name="write_to_file",
                arguments='{"file_path": "loop.txt", "content": "1", "overwrite": true}',
            )
        ],
        finish_reason="tool_calls",
    )

    class InfiniteLoopAdapter(MockLLMAdapter):
        async def stream(
            self,
            messages: list[Any],
            tools: list[dict[str, Any]] | None = None,
        ) -> Any:
            yield infinite_tool_chunk

    loop = AgentLoop(
        context=ctx,
        session=session,
        llm_adapter=InfiniteLoopAdapter(),
        tool_registry=registry,
    )

    tokens = []
    async for tok in loop.run_turn("Loop forever", options=TurnOptions(max_iterations=3)):
        tokens.append(tok)

    full_output = "".join(tokens)
    assert "[Warning: Reached maximum turn iterations limit (3)]" in full_output
