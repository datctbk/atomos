from pathlib import Path

from atomos.agent.loop import AgentLoop
from atomos.boot.bundles.base import CoreBundle, LLMBundle, ToolsBundle
from atomos.boot.profile import Profile
from atomos.core.context import Context
from atomos.core.session import Session, SessionStore
from atomos.llm.base import BaseLLMAdapter
from atomos.llm.providers.deepseek import DeepSeekAdapter
from atomos.llm.providers.openai import OpenAIAdapter
from atomos.tools.base import ToolRegistry


def test_bundles_application(tmp_path: Path) -> None:
    ctx = Context()
    core = CoreBundle(sessions_dir=tmp_path)
    tools = ToolsBundle(workspace_root=tmp_path)
    llm = LLMBundle(model="deepseek-chat")

    d_core = core.apply(ctx)
    d_tools = tools.apply(ctx)
    d_llm = llm.apply(ctx)

    assert ctx.has(SessionStore)
    assert ctx.has(Session)
    assert ctx.has(ToolRegistry)
    assert ctx.has(BaseLLMAdapter)
    assert isinstance(ctx.get(BaseLLMAdapter), DeepSeekAdapter)

    # Test clean unbinding
    d_core.dispose()
    d_tools.dispose()
    d_llm.dispose()


def test_profile_bootstrap_local(tmp_path: Path) -> None:
    profile = Profile(
        is_local=True,
        local_url="http://localhost:11434/v1",
        workspace_dir=tmp_path,
        sessions_dir=tmp_path,
    )

    ctx, session, loop = profile.bootstrap()
    assert isinstance(ctx, Context)
    assert isinstance(session, Session)
    assert isinstance(loop, AgentLoop)
    assert isinstance(ctx.get(BaseLLMAdapter), OpenAIAdapter)
    assert ctx.get(BaseLLMAdapter).is_local is True
