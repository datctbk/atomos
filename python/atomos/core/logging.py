"""Logging subsystem with automated token and secret redaction for Atomos (SECURITY-03)."""

from __future__ import annotations

import logging
import re
from typing import Any

# Regex patterns matching sensitive credentials, tokens, and keys
REDACTION_PATTERNS = [
    re.compile(r"(sk-[a-zA-Z0-9_\-]{20,})"),
    re.compile(r"(Bearer\s+[a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE),
    re.compile(r"((?:password|secret|token|api_key|apikey)\s*=\s*['\"][^'\"]+['\"])", re.IGNORECASE),
]


class RedactionFilter(logging.Filter):
    """Logging filter that sanitizes and masks sensitive API keys and secrets in messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            sanitized = record.msg
            for pattern in REDACTION_PATTERNS:
                sanitized = pattern.sub("***MASKED***", sanitized)
            record.msg = sanitized

        if record.args:
            if isinstance(record.args, dict):
                clean_args: dict[str, Any] = {}
                for k, v in record.args.items():
                    val_str = str(v)
                    for pattern in REDACTION_PATTERNS:
                        val_str = pattern.sub("***MASKED***", val_str)
                    clean_args[k] = val_str
                record.args = clean_args
            elif isinstance(record.args, tuple):
                new_args: list[Any] = []
                for item in record.args:
                    val_str = str(item)
                    for pattern in REDACTION_PATTERNS:
                        val_str = pattern.sub("***MASKED***", val_str)
                    new_args.append(val_str)
                record.args = tuple(new_args)

        return True


def get_logger(name: str = "atomos") -> logging.Logger:
    """Obtain a logger instance pre-configured with the RedactionFilter."""
    logger = logging.getLogger(name)
    if not any(isinstance(f, RedactionFilter) for f in logger.filters):
        logger.addFilter(RedactionFilter())
    return logger
