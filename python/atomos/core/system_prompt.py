"""Dynamic system prompt synthesis with environment context, workspace path, and safety guardrails."""

from __future__ import annotations

import os
import platform
from pathlib import Path


def build_system_prompt(
    workspace_path: Path | str | None = None,
    custom_instructions: str | None = None,
    tools_summary: str | None = None,
) -> str:
    """Constructs a comprehensive system prompt injected with host environment metadata."""
    resolved_workspace = Path(workspace_path or Path.cwd()).expanduser().resolve()
    os_name = platform.system()
    os_release = platform.release()
    shell_name = os.environ.get("SHELL", "bash")

    base_prompt = (
        "You are Atomos, a powerful, state-of-the-art agentic AI coding assistant.\n"
        "You help developers inspect codebases, execute terminal workflows, and write high-quality code.\n\n"
        f"### Environment Information\n"
        f"- Operating System: {os_name} ({os_release})\n"
        f"- Shell: {shell_name}\n"
        f"- Current Workspace Root: {resolved_workspace}\n\n"
        "### Operational Guardrails\n"
        "1. Always prefer inspecting files before modifying them.\n"
        "2. When editing files, provide exact substring replacements.\n"
        "3. Respect workspace boundaries. Do not attempt to access or modify files outside the workspace root.\n"
        "4. Avoid destructive or runaway operations.\n"
    )

    if tools_summary:
        base_prompt += f"\n### Available Capabilities\n{tools_summary}\n"

    if custom_instructions:
        base_prompt += f"\n### Custom Instructions\n{custom_instructions}\n"

    return base_prompt.strip()
