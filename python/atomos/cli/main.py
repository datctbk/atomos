"""Atomos CLI: Terminal interface and interactive agent REPL."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from atomos.agent.loop import AgentLoop, TurnOptions
from atomos.boot.profile import Profile
from atomos.core.context import Context
from atomos.tools.guardrails import (
    ApprovalCallback,
    GuardrailDecision,
    GuardrailMode,
    RiskLevel,
    ToolGuardrailClassifier,
)

app = typer.Typer(
    name="atomos",
    help="Atomos - Python AI Agent Harness powered by Cordis micro-kernel patterns.",
    no_args_is_help=False,
)
console = Console()


def _format_error(title: str, message: str) -> None:
    console.print(
        Panel(
            f"[bold red]{title}[/bold red]\n\n{message}",
            title="[bold red]Error[/bold red]",
            border_style="red",
        )
    )


def _create_approval_callback(classifier: ToolGuardrailClassifier, is_tty: bool) -> ApprovalCallback:
    async def approval_callback(decision: GuardrailDecision) -> bool:
        if not is_tty:
            return False

        risk_color = {
            RiskLevel.SAFE: "green",
            RiskLevel.LOW: "cyan",
            RiskLevel.HIGH: "yellow",
            RiskLevel.CRITICAL: "bold red",
        }.get(decision.risk_level, "yellow")

        info_lines = [
            f"[bold]Tool:[/bold]         [cyan]{decision.tool_name}[/cyan]",
            f"[bold]Command/File:[/bold] [white]{decision.command_or_target}[/white]",
            f"[bold]Risk Level:[/bold]   [{risk_color}]{decision.risk_level.value.upper()}[/{risk_color}]",
            f"[bold]Reason:[/bold]       [dim]{decision.reason}[/dim]",
        ]

        console.print(
            Panel(
                "\n".join(info_lines),
                title=f"[{risk_color}]⚠️  Security Guardrail: Confirmation Required[/{risk_color}]",
                border_style=risk_color,
            )
        )

        try:
            choice = Prompt.ask(
                "[bold yellow]Approve execution?[/bold yellow] ([green]y[/green]es / [red]N[/red]o / [cyan]a[/cyan]lways allow / [magenta]abort[/magenta])",
                default="n",
            ).strip().lower()

            if choice in {"y", "yes"}:
                return True
            elif choice in {"a", "always"}:
                if decision.tool_name == "run_command" and decision.command_or_target:
                    classifier.whitelist_command(decision.command_or_target)
                else:
                    classifier.whitelist_tool(decision.tool_name)
                console.print("  [dim green]✔ Added to session whitelist.[/dim green]")
                return True
            elif choice == "abort":
                raise KeyboardInterrupt()
            else:
                return False
        except (KeyboardInterrupt, EOFError):
            return False

    return approval_callback


async def _run_agent_turn(
    loop: AgentLoop,
    prompt_text: str,
    options: TurnOptions | None = None,
    is_tty: bool = True,
    live: bool = False,
    markdown: bool = False,
) -> str:
    accumulated = ""
    if (live or markdown) and is_tty:
        with Live(console=console, refresh_per_second=15, vertical_overflow="visible") as live_display:
            async for token in loop.run_turn(prompt_text, options=options):
                accumulated += token
                if markdown:
                    live_display.update(Markdown(accumulated))
                else:
                    live_display.update(Text.from_ansi(accumulated))
    else:
        async for token in loop.run_turn(prompt_text, options=options):
            accumulated += token
            sys.stdout.write(token)
            sys.stdout.flush()
        sys.stdout.write("\n")
    return accumulated


def _attach_event_listeners(ctx: Context, is_tty: bool) -> None:
    if not is_tty:
        return

    def on_tool_start(ev: Any) -> None:
        data = ev.payload if hasattr(ev, "payload") else (ev if isinstance(ev, dict) else {})
        name = data.get("name", "unknown")
        raw_args = data.get("args", {})
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except (json.JSONDecodeError, TypeError):
                args = {"raw": raw_args}
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            args = {}

        console.print(f"\n[bold yellow]⚡ Running tool:[/bold yellow] [bold cyan]{name}[/bold cyan]")
        if name == "run_command":
            cmd = args.get("command", "")
            cwd = args.get("cwd")
            cwd_str = f" [dim](cwd: {cwd})[/dim]" if cwd else ""
            console.print(f"  [bold white]$[/bold white] [bold green]{cmd}[/bold green]{cwd_str}")
        elif name == "view_file":
            path = args.get("file_path", "")
            offset = args.get("offset", 1)
            limit = args.get("limit", 800)
            console.print(f"  [dim]📄[/dim] [blue]{path}[/blue] [dim](lines {offset}-{offset+limit-1})[/dim]")
        elif name == "write_file":
            path = args.get("file_path", "")
            console.print(f"  [dim]📝[/dim] [blue]{path}[/blue]")
        elif name == "replace_file":
            path = args.get("file_path", "")
            console.print(f"  [dim]✏️[/dim] [blue]{path}[/blue]")
        elif args:
            compact_args = ", ".join(f"{k}={v!r}" for k, v in args.items() if k != "content")
            if compact_args:
                console.print(f"  [dim]({compact_args})[/dim]")

    def on_tool_end(ev: Any) -> None:
        data = ev.payload if hasattr(ev, "payload") else (ev if isinstance(ev, dict) else {})
        result = data.get("result", {})
        success = result.get("success", False) if isinstance(result, dict) else False
        error = result.get("error") if isinstance(result, dict) else None
        meta = result.get("metadata", {}) if isinstance(result, dict) else {}
        time_ms = meta.get("execution_time_ms") if isinstance(meta, dict) else None
        duration_str = f" [dim]({time_ms:.1f}ms)[/dim]" if time_ms is not None else ""

        if success:
            console.print(f"  [green]✔ Success[/green]{duration_str}")
        else:
            err_msg = f": [red]{error}[/red]" if error else ""
            console.print(f"  [red]✖ Failed[/red]{err_msg}{duration_str}")

    ctx.on("agent/tool_start", on_tool_start)
    ctx.on("agent/tool_end", on_tool_end)


@app.command()
def main(
    prompt: Annotated[
        str | None,
        typer.Argument(help="Optional single-turn prompt to run non-interactively."),
    ] = None,
    local: Annotated[
        bool,
        typer.Option("--local", "-l", help="Run with local OpenAI-compatible LLM (e.g. Ollama)."),
    ] = False,
    model: Annotated[
        str | None,
        typer.Option("--model", "-m", help="Target LLM model name."),
    ] = None,
    local_url: Annotated[
        str | None,
        typer.Option("--local-url", help="Local LLM endpoint URL (defaults to ATOMOS_LOCAL_LLM_URL or http://localhost:11434/v1)."),
    ] = None,
    workspace: Annotated[
        Path | None,
        typer.Option("--workspace", "-w", help="Workspace root directory."),
    ] = None,
    system_prompt: Annotated[
        str,
        typer.Option("--system-prompt", help="Custom system instructions."),
    ] = "",
    live: Annotated[
        bool,
        typer.Option("--live", help="Use Rich Live display mode during streaming."),
    ] = False,
    markdown: Annotated[
        bool,
        typer.Option("--markdown", "--md", help="Render response formatted with Rich Markdown."),
    ] = False,
    guardrail: Annotated[
        GuardrailMode,
        typer.Option(
            "--guardrail",
            "-g",
            help="Safety guardrail mode: 'ask-dangerous' (default), 'ask-always', or 'yolo'.",
            case_sensitive=False,
        ),
    ] = GuardrailMode.ASK_DANGEROUS,
) -> None:
    """Execute Atomos agent turns or start an interactive session."""
    target_model = model or ("deepseek-r1" if local else "deepseek-chat")
    is_tty = sys.stdout.isatty()
    workspace_dir = workspace.expanduser().resolve() if workspace else Path.cwd().resolve()
    effective_local_url = local_url or os.environ.get("ATOMOS_LOCAL_LLM_URL", "http://localhost:11434/v1")

    # Verify API key only for cloud non-local runs
    if not local and not os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        _format_error(
            "Missing API Key",
            "Please set [bold green]DEEPSEEK_API_KEY[/bold green] (or [bold green]OPENAI_API_KEY[/bold green]), "
            "or use [bold cyan]--local / -l[/bold cyan] to connect to a local LLM runner (e.g. Ollama).",
        )
        raise typer.Exit(code=1)

    profile = Profile(
        model=target_model,
        is_local=local,
        local_url=effective_local_url,
        workspace_dir=workspace_dir,
        system_prompt=system_prompt,
        guardrail_mode=guardrail,
    )

    ctx, _session, loop = profile.bootstrap()
    classifier = ctx.get(ToolGuardrailClassifier)
    if classifier:
        loop.approval_callback = _create_approval_callback(classifier, is_tty=is_tty)

    _attach_event_listeners(ctx, is_tty=is_tty)
    turn_options = ctx.get(TurnOptions)

    # 1. Single-turn non-interactive execution
    if prompt:
        try:
            asyncio.run(
                _run_agent_turn(
                    loop,
                    prompt,
                    options=turn_options,
                    is_tty=is_tty,
                    live=live,
                    markdown=markdown,
                )
            )
        except (KeyboardInterrupt, asyncio.CancelledError):
            console.print("\n[bold yellow]⚠ Turn cancelled by user.[/bold yellow]")
            raise typer.Exit(code=130)
        except Exception as exc:
            _format_error("Execution Error", str(exc))
            raise typer.Exit(code=1) from exc
        finally:
            ctx.dispose()
        return

    # 2. Interactive REPL loop
    if is_tty:
        console.print(
            Panel.fit(
                f"[bold cyan]Atomos[/bold cyan] (AI-DLC Agentic Coding Assistant)\n"
                f"[dim]Model: {target_model} | Local: {local} | Live: {live} | Markdown: {markdown} | Workspace: {workspace_dir}[/dim]\n"
                f"[dim]Press Ctrl+C during streaming to cancel a prompt. Type 'exit', 'quit', or ':q' to leave.[/dim]",
                title="[bold green]Interactive Mode[/bold green]",
                border_style="cyan",
            )
        )

    try:
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]atomos>[/bold green]") if is_tty else sys.stdin.readline()
            except (KeyboardInterrupt, EOFError):
                if is_tty:
                    console.print("\n[dim]Goodbye![/dim]")
                break

            if not user_input or not user_input.strip():
                if not is_tty:
                    break
                continue

            cleaned = user_input.strip()
            if cleaned.lower() in {"exit", "quit", ":q"}:
                if is_tty:
                    console.print("[dim]Goodbye![/dim]")
                break

            try:
                asyncio.run(
                    _run_agent_turn(
                        loop,
                        cleaned,
                        options=turn_options,
                        is_tty=is_tty,
                        live=live,
                        markdown=markdown,
                    )
                )
            except (KeyboardInterrupt, asyncio.CancelledError):
                console.print("\n[bold yellow]⚠ Turn cancelled by user.[/bold yellow]")
            except Exception as exc:  # noqa: BLE001
                _format_error("Turn Error", str(exc))
    finally:
        ctx.dispose()


if __name__ == "__main__":
    app()
