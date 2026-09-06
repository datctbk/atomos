"""Atomos Programmatic Python SDK Client."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from types import TracebackType
from typing import Self

from atomos.agent.loop import AgentLoop, TurnOptions
from atomos.boot.profile import Profile
from atomos.core.context import Context
from atomos.core.session import Session


class AtomosClient:
    """Async context manager SDK for programmatic Atomos agent interactions."""

    def __init__(
        self,
        workspace: Path | str = ".",
        model: str = "deepseek-chat",
        is_local: bool = False,
        local_url: str = "http://localhost:11434/v1",
        system_prompt: str = "",
        sessions_dir: Path | str | None = None,
    ) -> None:
        self.profile = Profile(
            workspace_dir=Path(workspace).expanduser().resolve(),
            model=model,
            is_local=is_local,
            local_url=local_url,
            system_prompt=system_prompt,
            sessions_dir=Path(sessions_dir).expanduser() if sessions_dir else Path.home() / ".atomos" / "sessions",
        )
        self.context: Context | None = None
        self.session: Session | None = None
        self.loop: AgentLoop | None = None

    async def __aenter__(self) -> Self:
        self.context, self.session, self.loop = self.profile.bootstrap()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.context:
            self.context.dispose()
        self.context = None
        self.session = None
        self.loop = None

    async def chat(
        self,
        prompt: str,
        options: TurnOptions | None = None,
    ) -> AsyncIterator[str]:
        """Stream an agent turn response delta by delta."""
        if not self.loop or not self.context:
            raise RuntimeError(
                "AtomosClient must be entered using 'async with AtomosClient(...) as client:'."
            )
        turn_opts = options or self.context.get(TurnOptions)
        async for token in self.loop.run_turn(prompt, options=turn_opts):
            yield token
