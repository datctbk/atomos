"""Human-in-the-Loop Interactive Safety Guardrails and Risk Classification for Atomos."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class RiskLevel(str, Enum):
    """Risk severity classification for tool execution."""

    SAFE = "safe"
    LOW = "low"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailMode(str, Enum):
    """Guardrail policy execution modes."""

    ASK_DANGEROUS = "ask-dangerous"
    ASK_ALWAYS = "ask-always"
    YOLO = "yolo"


class GuardrailDecision(BaseModel):
    """Decision output from the guardrail risk assessment."""

    model_config = ConfigDict(frozen=True)

    risk_level: RiskLevel
    reason: str
    tool_name: str
    command_or_target: str = ""
    requires_approval: bool = False


# Type alias for async user confirmation callbacks: (decision) -> bool
ApprovalCallback = Callable[[GuardrailDecision], Coroutine[Any, Any, bool]]


class ToolGuardrailClassifier:
    """Evaluates tool invocation parameters and classifies operational risks."""

    # High-risk: Package manager installations & modifications
    PACKAGE_INSTALL_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\b(pip|pip3|uv\s+pip|poetry\s+add|conda|mamba)\s+(install|uninstall|download)\b", re.IGNORECASE),
        re.compile(r"\b(npm|yarn|pnpm|bun)\s+(install|i|add|remove|uninstall|update)\b", re.IGNORECASE),
        re.compile(r"\bnpx(\s+-[a-zA-Z0-9_\-]+)*\s+[a-zA-Z0-9_\-@/]+", re.IGNORECASE),
        re.compile(r"\b(brew|cargo|gem|go\s+install|apt|apt-get|apk|yum|pacman)\s+(install|remove|uninstall)\b", re.IGNORECASE),
    ]

    # Critical-risk: Destructive filesystem or git commands
    DESTRUCTIVE_COMMAND_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\brm\s+-[rfRF]+\b"),
        re.compile(r"\b(rmdir|unlink)\b"),
        re.compile(r"\bgit\s+(reset\s+--hard|clean\s+-[fdxFDX]+|push\s+.*--force)\b"),
        re.compile(r"\b(mkfs|dd\s+if=|fdisk|parted)\b"),
        re.compile(r"\bchmod\s+(-R\s+)?(777|666)\b"),
    ]

    # High-risk: Remote code piping and arbitrary downloads
    REMOTE_EXEC_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\b(curl|wget)\b.*\|\s*(bash|sh|zsh|python|python3)\b", re.IGNORECASE),
    ]

    # Sensitive configuration and credential files
    SENSITIVE_FILE_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"(^|/)(\.env|\.env\..*|id_rsa|id_ed25519|\.aws/credentials|\.kube/config)$", re.IGNORECASE),
        re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|pyproject\.toml|deployment\.ya?ml)$", re.IGNORECASE),
    ]

    def __init__(self, mode: GuardrailMode = GuardrailMode.ASK_DANGEROUS) -> None:
        self.mode = mode
        self._session_whitelisted_commands: set[str] = set()
        self._session_whitelisted_tools: set[str] = set()

    def whitelist_command(self, command: str) -> None:
        """Whitelist a specific command for the current session."""
        self._session_whitelisted_commands.add(command.strip())

    def whitelist_tool(self, tool_name: str) -> None:
        """Whitelist an entire tool for the current session."""
        self._session_whitelisted_tools.add(tool_name.strip())

    def evaluate(self, tool_name: str, raw_args: dict[str, Any] | str) -> GuardrailDecision:
        """Evaluate risk and determine if user approval is required."""
        args: dict[str, Any]
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except (json.JSONDecodeError, TypeError):
                args = {"raw": raw_args}
        else:
            args = raw_args

        # 1. Check session whitelist
        if tool_name in self._session_whitelisted_tools:
            return GuardrailDecision(
                risk_level=RiskLevel.SAFE,
                reason="Tool is session-whitelisted by user",
                tool_name=tool_name,
                requires_approval=False,
            )

        if tool_name == "run_command":
            cmd = str(args.get("command", "")).strip()
            if cmd in self._session_whitelisted_commands:
                return GuardrailDecision(
                    risk_level=RiskLevel.SAFE,
                    reason="Command is session-whitelisted by user",
                    tool_name=tool_name,
                    command_or_target=cmd,
                    requires_approval=False,
                )
            return self._evaluate_shell_command(cmd)

        if tool_name in {"write_file", "replace_file"}:
            path = str(args.get("file_path", "")).strip()
            return self._evaluate_file_write(tool_name, path)

        if tool_name == "view_file":
            path = str(args.get("file_path", "")).strip()
            return self._evaluate_file_read(path)

        # Default fallback for custom or external tools
        requires_approval = self.mode == GuardrailMode.ASK_ALWAYS
        return GuardrailDecision(
            risk_level=RiskLevel.LOW,
            reason=f"Standard invocation of tool '{tool_name}'",
            tool_name=tool_name,
            requires_approval=requires_approval,
        )

    def _evaluate_shell_command(self, command: str) -> GuardrailDecision:
        """Classify shell command risk."""
        # Check critical destructive patterns
        for pat in self.DESTRUCTIVE_COMMAND_PATTERNS:
            if pat.search(command):
                requires = self.mode in {GuardrailMode.ASK_DANGEROUS, GuardrailMode.ASK_ALWAYS}
                return GuardrailDecision(
                    risk_level=RiskLevel.CRITICAL,
                    reason="Destructive command detected (deletion, hard reset, or broad permission change)",
                    tool_name="run_command",
                    command_or_target=command,
                    requires_approval=requires,
                )

        # Check remote execution piping
        for pat in self.REMOTE_EXEC_PATTERNS:
            if pat.search(command):
                requires = self.mode in {GuardrailMode.ASK_DANGEROUS, GuardrailMode.ASK_ALWAYS}
                return GuardrailDecision(
                    risk_level=RiskLevel.HIGH,
                    reason="Remote code download and piped execution detected",
                    tool_name="run_command",
                    command_or_target=command,
                    requires_approval=requires,
                )

        # Check package manager installs
        for pat in self.PACKAGE_INSTALL_PATTERNS:
            if pat.search(command):
                requires = self.mode in {GuardrailMode.ASK_DANGEROUS, GuardrailMode.ASK_ALWAYS}
                return GuardrailDecision(
                    risk_level=RiskLevel.HIGH,
                    reason="Third-party package manager installation or modification",
                    tool_name="run_command",
                    command_or_target=command,
                    requires_approval=requires,
                )

        # Safe / Low risk shell command (e.g. ls, git status, pytest, echo)
        requires = self.mode == GuardrailMode.ASK_ALWAYS
        return GuardrailDecision(
            risk_level=RiskLevel.SAFE,
            reason="Standard shell command execution",
            tool_name="run_command",
            command_or_target=command,
            requires_approval=requires,
        )

    def _evaluate_file_write(self, tool_name: str, file_path: str) -> GuardrailDecision:
        """Classify file creation and replacement risk."""
        for pat in self.SENSITIVE_FILE_PATTERNS:
            if pat.search(file_path):
                requires = self.mode in {GuardrailMode.ASK_DANGEROUS, GuardrailMode.ASK_ALWAYS}
                return GuardrailDecision(
                    risk_level=RiskLevel.CRITICAL if ".env" in file_path or "id_" in file_path else RiskLevel.HIGH,
                    reason=f"Modifying sensitive configuration or credential file: {file_path}",
                    tool_name=tool_name,
                    command_or_target=file_path,
                    requires_approval=requires,
                )

        requires = self.mode == GuardrailMode.ASK_ALWAYS
        return GuardrailDecision(
            risk_level=RiskLevel.LOW,
            reason=f"File modification in workspace: {file_path}",
            tool_name=tool_name,
            command_or_target=file_path,
            requires_approval=requires,
        )

    def _evaluate_file_read(self, file_path: str) -> GuardrailDecision:
        """Classify file read risk."""
        if any(sens in file_path.lower() for sens in [".env", "id_rsa", "id_ed25519", "credentials"]):
            requires = self.mode == GuardrailMode.ASK_ALWAYS
            return GuardrailDecision(
                risk_level=RiskLevel.LOW,
                reason=f"Reading sensitive file: {file_path}",
                tool_name="view_file",
                command_or_target=file_path,
                requires_approval=requires,
            )

        requires = self.mode == GuardrailMode.ASK_ALWAYS
        return GuardrailDecision(
            risk_level=RiskLevel.SAFE,
            reason="Read-only file inspection",
            tool_name="view_file",
            command_or_target=file_path,
            requires_approval=requires,
        )
