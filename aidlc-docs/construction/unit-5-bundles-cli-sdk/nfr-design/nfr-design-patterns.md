# Unit 5 NFR Design Patterns: Bundles, CLI & SDK

This document details the concrete design patterns for profile bootstrapping, Typer CLI execution, Rich terminal rendering, and the async SDK context manager.

---

## 1. Bundle & Profile Bootstrap Pattern

```python
class Profile(BaseModel):
    """Central container configuration model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: str = "deepseek-chat"
    is_local: bool = False
    local_url: str = "http://localhost:11434/v1"
    workspace_dir: Path = Field(default_factory=Path.cwd)
    sessions_dir: Path = Field(default_factory=lambda: Path.home() / ".atomos" / "sessions")
    system_prompt: str = ""

    def bootstrap(self) -> tuple[Context, Session, AgentLoop]:
        """Wires up Context, Session, ToolRegistry, LLMAdapter, and AgentLoop."""
        ctx = Context()

        # 1. Initialize core storage
        store = SessionStore(base_dir=self.sessions_dir)
        session = store.create_session()
        ctx.provide(Session, session)
        ctx.provide(SessionStore, store)

        # 2. Initialize Tool Registry and Builtin Tools
        sandbox = PathSandbox(workspace_root=self.workspace_dir)
        tool_reg = ToolRegistry()
        tool_reg.register_tool(ViewFileTool(sandbox=sandbox))
        tool_reg.register_tool(WriteFileTool(sandbox=sandbox))
        tool_reg.register_tool(ReplaceFileTool(sandbox=sandbox))
        tool_reg.register_tool(RunCommandTool(workspace_root=self.workspace_dir))
        ctx.provide(ToolRegistry, tool_reg)

        # 3. Initialize LLM Adapter
        adapter: BaseLLMAdapter
        if self.is_local:
            adapter = OpenAIAdapter(
                model=self.model if self.model != "deepseek-chat" else "deepseek-r1",
                base_url=self.local_url,
                is_local=True,
            )
        else:
            adapter = DeepSeekAdapter(model=self.model)
        ctx.provide(BaseLLMAdapter, adapter)

        # 4. Synthesize system prompt and assemble loop
        sys_prompt = self.system_prompt or build_system_prompt(
            workspace_path=self.workspace_dir,
            tools_summary="File manipulation (view, write, replace) and shell command execution.",
        )
        loop = AgentLoop(
            context=ctx,
            session=session,
            llm_adapter=adapter,
            tool_registry=tool_reg,
        )
        ctx.provide(AgentLoop, loop)

        return ctx, session, loop
```

---

## 2. Interactive CLI REPL with Rich Rendering Pattern

```python
def run_interactive_cli(profile: Profile, initial_prompt: str | None = None) -> None:
    """Runs the Rich-enhanced interactive REPL loop."""
    console = Console()
    ctx, session, loop = profile.bootstrap()

    console.print(Panel.fit(
        f"[bold cyan]Atomos[/bold cyan] (AI-DLC Agentic Coding Assistant)\n"
        f"[dim]Model: {profile.model} | Workspace: {profile.workspace_dir} | Local: {profile.is_local}[/dim]",
        border_style="cyan",
    ))

    # Real-time event listeners for tool panels
    ctx.on("agent/tool_start", lambda ev: console.print(f"[yellow]⚡ Calling tool:[/yellow] [bold]{ev.payload.get('name')}[/bold]"))
    ctx.on("agent/tool_end", lambda ev: console.print(f"[green]✔ Tool completed[/green]"))

    async def execute_turn(prompt_text: str):
        with Live(console=console, refresh_per_second=15) as live:
            accumulated = ""
            async for token in loop.run_turn(prompt_text):
                accumulated += token
                live.update(Markdown(accumulated))

    if initial_prompt:
        asyncio.run(execute_turn(initial_prompt))

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]atomos>[/bold green]")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in {"exit", "quit", ":q"}:
                console.print("[dim]Goodbye![/dim]")
                break
            asyncio.run(execute_turn(user_input))
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Session closed.[/dim]")
            break
```

---

## 3. Programmatic SDK Client Pattern

```python
class AtomosClient:
    """Async context manager SDK for programmatic Atomos agent interactions."""

    def __init__(
        self,
        workspace: Path | str = ".",
        model: str = "deepseek-chat",
        is_local: bool = False,
        local_url: str = "http://localhost:11434/v1",
        system_prompt: str = "",
    ) -> None:
        self.profile = Profile(
            workspace_dir=Path(workspace).resolve(),
            model=model,
            is_local=is_local,
            local_url=local_url,
            system_prompt=system_prompt,
        )
        self.context: Context | None = None
        self.session: Session | None = None
        self.loop: AgentLoop | None = None

    async def __aenter__(self) -> AtomosClient:
        self.context, self.session, self.loop = self.profile.bootstrap()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.context:
            self.context.dispose()

    async def chat(self, prompt: str) -> AsyncIterator[str]:
        if not self.loop:
            raise RuntimeError("AtomosClient must be entered using 'async with AtomosClient(...)'.")
        async for token in self.loop.run_turn(prompt):
            yield token
```
