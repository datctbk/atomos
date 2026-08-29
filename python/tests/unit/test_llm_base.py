import pytest

from atomos.llm.base import (
    LLMMessage,
    LLMRole,
    ToolCallAccumulator,
    ToolCallFragment,
)
from atomos.llm.mock import MockLLMAdapter


def test_llm_message_creation() -> None:
    msg = LLMMessage(role=LLMRole.USER, content="Hello Atomos")
    assert msg.role == LLMRole.USER
    assert msg.content == "Hello Atomos"
    assert msg.tool_calls is None


def test_tool_call_accumulator() -> None:
    acc = ToolCallAccumulator()

    # Stream fragments for tool call #0
    acc.add_fragment(ToolCallFragment(index=0, id="call_1", name="view_file", arguments='{"file_'))
    acc.add_fragment(ToolCallFragment(index=0, arguments='path": "test.txt"}'))

    # Stream fragments for tool call #1
    acc.add_fragment(ToolCallFragment(index=1, id="call_2", name="run_cmd", arguments='{"cmd": "ls"}'))

    tool_calls = acc.get_tool_calls()
    assert len(tool_calls) == 2

    assert tool_calls[0]["id"] == "call_1"
    assert tool_calls[0]["function"]["name"] == "view_file"
    assert tool_calls[0]["function"]["arguments"] == '{"file_path": "test.txt"}'

    assert tool_calls[1]["id"] == "call_2"
    assert tool_calls[1]["function"]["name"] == "run_cmd"
    assert tool_calls[1]["function"]["arguments"] == '{"cmd": "ls"}'


@pytest.mark.asyncio
async def test_mock_llm_adapter_stream() -> None:
    adapter = MockLLMAdapter(canned_text="Hello from mock adapter")
    chunks = []
    async for chunk in adapter.stream([LLMMessage(role=LLMRole.USER, content="hi")]):
        chunks.append(chunk)

    assert len(chunks) == 4
    full_text = "".join(c.delta_content for c in chunks)
    assert full_text == "Hello from mock adapter"
    assert chunks[-1].finish_reason == "stop"
    assert chunks[-1].usage is not None
