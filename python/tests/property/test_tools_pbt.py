import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from atomos.tools.builtins.fs import PathSandbox, SecurityAccessError


@st.composite
def escaping_paths(draw: st.DrawFn) -> str:
    """Generates paths with varying numbers of parent directory hops."""
    hops = draw(st.integers(min_value=5, max_value=20))
    file_name = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=8))
    traversal = "/".join([".."] * hops) + f"/{file_name}.txt"
    return traversal


@given(path_str=escaping_paths())
def test_prop_path_confinement_sandbox(path_str: str) -> None:
    """PBT-01 & SECURITY-05: Fuzzing arbitrary traversal strings strictly raises SecurityAccessError."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox = PathSandbox(workspace_root=Path(tmp_dir))
        try:
            sandbox.resolve_safe_path(path_str)
            # If resolve_safe_path didn't raise, verify that the path is actually inside workspace
            resolved = (Path(tmp_dir) / path_str).resolve()
            assert resolved.is_relative_to(Path(tmp_dir).resolve())
        except SecurityAccessError:
            pass  # Expected and required for escaping traversals
