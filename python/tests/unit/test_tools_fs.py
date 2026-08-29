from pathlib import Path

import pytest

from atomos.tools.builtins.fs import (
    PathSandbox,
    ReplaceFileInput,
    ReplaceFileTool,
    SecurityAccessError,
    ViewFileInput,
    ViewFileTool,
    WriteFileInput,
    WriteFileTool,
)


def test_path_sandbox_confinement(tmp_path: Path) -> None:
    sandbox = PathSandbox(workspace_root=tmp_path)

    # Valid relative path
    safe = sandbox.resolve_safe_path("src/main.py")
    assert safe == (tmp_path / "src/main.py").resolve()

    # Traversal attempt escaping workspace root
    with pytest.raises(SecurityAccessError, match="outside authorized workspace root"):
        sandbox.resolve_safe_path("../../etc/passwd")


@pytest.mark.asyncio
async def test_fs_tools_lifecycle(tmp_path: Path) -> None:
    sandbox = PathSandbox(workspace_root=tmp_path)
    view_tool = ViewFileTool(sandbox=sandbox)
    write_tool = WriteFileTool(sandbox=sandbox)
    replace_tool = ReplaceFileTool(sandbox=sandbox)

    # 1. Write file
    w_res = await write_tool.execute(
        WriteFileInput(file_path="hello.txt", content="Hello World\nLine 2\nLine 3")
    )
    assert w_res.success
    assert (tmp_path / "hello.txt").exists()

    # Write again without overwrite fails
    w_res_dup = await write_tool.execute(
        WriteFileInput(file_path="hello.txt", content="New content", overwrite=False)
    )
    assert not w_res_dup.success
    assert "FileExistsError" in str(w_res_dup.error)

    # 2. View file
    v_res = await view_tool.execute(ViewFileInput(file_path="hello.txt", offset=1, limit=2))
    assert v_res.success
    assert "Hello World" in v_res.output
    assert "Line 2" in v_res.output

    # 3. Replace file content
    r_res = await replace_tool.execute(
        ReplaceFileInput(file_path="hello.txt", old_string="Hello World", new_string="Hello Atomos")
    )
    assert r_res.success
    assert "Hello Atomos" in (tmp_path / "hello.txt").read_text()


@pytest.mark.asyncio
async def test_fs_tools_sandbox_security_blocking(tmp_path: Path) -> None:
    sandbox = PathSandbox(workspace_root=tmp_path)
    view_tool = ViewFileTool(sandbox=sandbox)

    res = await view_tool.execute(ViewFileInput(file_path="../../../outside.txt"))
    assert not res.success
    assert "SecurityAccessError" in str(res.error)
