from pathlib import Path

import pytest

from atomos.tools.builtins.fs import PathSandbox
from atomos.tools.builtins.shell import RunCommandInput, RunCommandTool


@pytest.mark.asyncio
async def test_run_command_success(tmp_path: Path) -> None:
    sandbox = PathSandbox(workspace_root=tmp_path)
    tool = RunCommandTool(sandbox=sandbox)

    res = await tool.execute(RunCommandInput(command="echo 'atomos test'"))
    assert res.success
    assert "atomos test" in res.output
    assert res.error is None


@pytest.mark.asyncio
async def test_run_command_failing_exit_code(tmp_path: Path) -> None:
    sandbox = PathSandbox(workspace_root=tmp_path)
    tool = RunCommandTool(sandbox=sandbox)

    res = await tool.execute(RunCommandInput(command="exit 42"))
    assert not res.success
    assert "42" in str(res.error)


@pytest.mark.asyncio
async def test_run_command_timeout_termination(tmp_path: Path) -> None:
    sandbox = PathSandbox(workspace_root=tmp_path)
    tool = RunCommandTool(sandbox=sandbox)

    res = await tool.execute(RunCommandInput(command="sleep 5", timeout_seconds=1))
    assert not res.success
    assert "timed out after 1 seconds" in str(res.error)
