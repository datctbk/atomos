import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from atomos.agent.loop import AgentLoop, TurnOptions
from atomos.boot.bundles.base import (
    CoreBundle,
    GuardrailsBundle,
    LLMBundle,
    ToolsBundle,
)
from atomos.core.context import Context
from atomos.core.session import Session
from atomos.core.system_prompt import build_system_prompt
from atomos.llm.base import BaseLLMAdapter
from atomos.tools.base import ToolRegistry
from atomos.tools.guardrails import GuardrailMode, ToolGuardrailClassifier


class Profile(BaseModel):
    """Central container configuration model for Atomos runtime."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: str = "deepseek-chat"
    is_local: bool = False
    local_url: str = Field(
        default_factory=lambda: os.environ.get("ATOMOS_LOCAL_LLM_URL", "http://localhost:11434/v1")
    )
    workspace_dir: Path = Field(default_factory=Path.cwd)
    sessions_dir: Path = Field(default_factory=lambda: Path.home() / ".atomos" / "sessions")
    system_prompt: str = ""
    guardrail_mode: GuardrailMode = GuardrailMode.ASK_DANGEROUS

    def bootstrap(self) -> tuple[Context, Session, AgentLoop]:
        """Wires up Context, Session, ToolRegistry, LLMAdapter, and AgentLoop."""
        ctx = Context()

        # 1. Apply core, tools, LLM, and guardrails bundles
        CoreBundle(sessions_dir=self.sessions_dir).apply(ctx)
        ToolsBundle(workspace_root=self.workspace_dir).apply(ctx)
        LLMBundle(model=self.model, is_local=self.is_local, local_url=self.local_url).apply(ctx)
        GuardrailsBundle(mode=self.guardrail_mode).apply(ctx)

        # 2. Retrieve injected services uniformly from Context
        session = ctx.get(Session)
        adapter = ctx.get(BaseLLMAdapter)
        registry = ctx.get(ToolRegistry)
        classifier = ctx.get(ToolGuardrailClassifier)

        # 3. Build system prompt if not explicitly supplied
        effective_system_prompt = self.system_prompt or build_system_prompt(
            workspace_path=self.workspace_dir,
            tools_summary="File manipulation (view, write, replace) and subprocess shell command execution.",
        )

        # 4. Assemble AgentLoop
        loop = AgentLoop(
            context=ctx,
            session=session,
            llm_adapter=adapter,
            tool_registry=registry,
            guardrail_classifier=classifier,
        )
        ctx.provide(AgentLoop, loop)
        ctx.provide(TurnOptions, TurnOptions(system_prompt=effective_system_prompt))

        return ctx, session, loop
