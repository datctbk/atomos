"""Security and guardrail data models and risk classification types for Atomos."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class RiskLevel(str, Enum):
    """Risk severity classification for tool execution and operational actions."""

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
