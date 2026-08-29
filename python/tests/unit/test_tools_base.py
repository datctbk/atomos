
import pytest
from pydantic import BaseModel, Field

from atomos.tools.base import BaseTool, ToolRegistry, ToolResult, truncate_output


class SampleInput(BaseModel):
    query: str = Field(description="Search query string.")
    limit: int = Field(default=10, description="Max results.")


class SampleTool(BaseTool[SampleInput]):
    def __init__(self) -> None:
        super().__init__(
            name="sample_tool",
            description="Sample demonstration tool.",
            params_model=SampleInput,
        )

    async def execute(self, params: SampleInput) -> ToolResult:
        if params.query == "error":
            raise RuntimeError("Forced tool error")
        return ToolResult(
            success=True,
            output=f"Results for '{params.query}' (limit={params.limit})",
            error=None,
        )


def test_base_tool_openai_schema() -> None:
    tool = SampleTool()
    schema = tool.to_openai_tool()
    assert schema["type"] == "function"
    func = schema["function"]
    assert func["name"] == "sample_tool"
    assert func["description"] == "Sample demonstration tool."
    params = func["parameters"]
    assert "query" in params["properties"]
    assert "limit" in params["properties"]


def test_tool_registry_registration_and_disposal() -> None:
    registry = ToolRegistry()
    tool = SampleTool()
    disposable = registry.register_tool(tool)

    assert registry.get_tool("sample_tool") is tool
    assert len(registry.list_tools()) == 1

    disposable.dispose()
    assert registry.get_tool("sample_tool") is None
    assert len(registry.list_tools()) == 0


@pytest.mark.asyncio
async def test_tool_registry_execution_success() -> None:
    registry = ToolRegistry()
    registry.register_tool(SampleTool())

    res = await registry.execute_tool("sample_tool", '{"query": "atomos", "limit": 5}')
    assert res.success
    assert res.output == "Results for 'atomos' (limit=5)"
    assert res.error is None


@pytest.mark.asyncio
async def test_tool_registry_execution_validation_error() -> None:
    registry = ToolRegistry()
    registry.register_tool(SampleTool())

    res = await registry.execute_tool("sample_tool", '{"invalid_field": 123}')
    assert not res.success
    assert "ValidationError" in str(res.error)


@pytest.mark.asyncio
async def test_tool_registry_execution_exception_sanitization() -> None:
    registry = ToolRegistry()
    registry.register_tool(SampleTool())

    res = await registry.execute_tool("sample_tool", '{"query": "error"}')
    assert not res.success
    assert "RuntimeError: Forced tool error" in str(res.error)


def test_truncate_output() -> None:
    # Line truncation
    many_lines = "\n".join(f"Line {i}" for i in range(1000))
    truncated_lines = truncate_output(many_lines, max_lines=10)
    assert "[Output truncated: showing first 10 lines]" in truncated_lines
    assert len(truncated_lines.splitlines()) == 12

    # Byte truncation
    large_text = "A" * 60_000
    truncated_bytes = truncate_output(large_text, max_lines=10_000, max_bytes=1000)
    assert "[Output truncated: capped at 1KB]" in truncated_bytes
