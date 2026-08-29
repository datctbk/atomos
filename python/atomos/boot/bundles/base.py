"""Base bundle composition and lifecycle mounting interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from atomos.core.context import Context, Disposable
from atomos.core.session import Session, SessionStore
from atomos.llm.base import BaseLLMAdapter
from atomos.llm.providers.deepseek import DeepSeekAdapter
from atomos.llm.providers.openai import OpenAIAdapter
from atomos.tools.base import ToolRegistry
from atomos.tools.builtins.fs import PathSandbox, ReplaceFileTool, ViewFileTool, WriteFileTool
from atomos.tools.builtins.shell import RunCommandTool


class BaseBundle(ABC):
    """Abstract lifecycle plugin mounting services and listeners to Context."""

    name: str = "base"

    @abstractmethod
    def apply(self, context: Context, **kwargs: Any) -> Disposable:
        """Mount bundle services and return a disposable unbinder."""
        ...


class CoreBundle(BaseBundle):
    """Mounts session storage and event filtering."""

    name: str = "core"

    def __init__(self, sessions_dir: Path | str | None = None) -> None:
        self.sessions_dir = Path(sessions_dir or Path.home() / ".atomos" / "sessions")

    def apply(self, context: Context, **kwargs: Any) -> Disposable:
        from atomos.core.context import CallbackDisposable

        store = SessionStore(base_dir=self.sessions_dir)
        session = store.create_session()
        d1 = context.provide(SessionStore, store)
        d2 = context.provide(Session, session)

        def _dispose() -> None:
            d1.dispose()
            d2.dispose()

        return CallbackDisposable(_dispose)


class ToolsBundle(BaseBundle):
    """Mounts built-in file and shell execution tools."""

    name: str = "tools"

    def __init__(self, workspace_root: Path | str | None = None) -> None:
        self.workspace_root = Path(workspace_root or Path.cwd()).resolve()

    def apply(self, context: Context, **kwargs: Any) -> Disposable:
        sandbox = PathSandbox(workspace_root=self.workspace_root)
        registry = ToolRegistry()
        registry.register_tool(ViewFileTool(sandbox=sandbox))
        registry.register_tool(WriteFileTool(sandbox=sandbox))
        registry.register_tool(ReplaceFileTool(sandbox=sandbox))
        registry.register_tool(RunCommandTool(sandbox=sandbox))
        return context.provide(ToolRegistry, registry)


class LLMBundle(BaseBundle):
    """Mounts LLM provider adapters (Cloud DeepSeek / Cloud or Local OpenAI)."""

    name: str = "llm"

    def __init__(
        self,
        model: str = "deepseek-chat",
        is_local: bool = False,
        local_url: str = "http://localhost:11434/v1",
    ) -> None:
        self.model = model
        self.is_local = is_local
        self.local_url = local_url

    def apply(self, context: Context, **kwargs: Any) -> Disposable:
        adapter: BaseLLMAdapter
        if self.is_local:
            adapter = OpenAIAdapter(
                model=self.model if self.model != "deepseek-chat" else "deepseek-r1",
                base_url=self.local_url,
                is_local=True,
            )
        else:
            adapter = DeepSeekAdapter(model=self.model)
        return context.provide(BaseLLMAdapter, adapter)
