# Unit 1 NFR Design Patterns: Core Kernel & Event Sourcing Store

This document specifies the concrete design patterns implementing performance, security, and resiliency for Unit 1.

---

## 1. Resilience Patterns: Buffered File Append & Synchronous Flush (`RES-03`)

### 1.1 Atomic Event Writer Pattern
```python
import os
from pathlib import Path

class AtomicEventWriter:
    """Manages secure, append-only JSONL event persistence with OS sync."""
    def __init__(self, file_path: Path):
        self.file_path = file_path
        # Ensure parent directory exists with 0o700 permissions (SECURITY-01)
        self.file_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Open file with mode 0o600
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        self._fd = os.open(str(self.file_path), flags, 0o600)
        self._file = open(self._fd, "w", encoding="utf-8", buffering=1) # Line buffered

    def append_line(self, line: str) -> None:
        self._file.write(line + "\n")
        self._file.flush()
        os.fsync(self._fd) # Synchronize to physical storage (RES-03)

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()
```

---

## 2. Security Patterns: Automated Redaction Filter (`SECURITY-03`)

### 2.1 Regex-Based Credential Masking Filter
```python
import re
import logging

REDACTION_PATTERNS = [
    re.compile(r"(sk-[a-zA-Z0-9_\-]{20,})"),                # OpenAI/DeepSeek API keys
    re.compile(r"(Bearer\s+[a-zA-Z0-9_\-\.]{20,})", re.I),  # Authorization Bearer tokens
    re.compile(r"(password|secret|token)\s*=\s*['\"][^'\"]+['\"]", re.I),
]

class RedactionFilter(logging.Filter):
    """Inspects all log messages and replaces sensitive API keys/tokens with ***MASKED***."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in REDACTION_PATTERNS:
                record.msg = pattern.sub(r"***MASKED***", record.msg)
        return True
```

---

## 3. Property-Based Testing Strategy Patterns (`PBT-01`, `PBT-02`)

### 3.1 Hypothesis Composite Strategies for SessionEvent
```python
from hypothesis import strategies as st
from datetime import datetime, timezone
from atomos.core.session import SessionEvent, SessionEventType

@st.composite
def session_events(draw) -> SessionEvent:
    event_id = draw(st.uuids()).hex
    session_id = draw(st.uuids()).hex
    seq = draw(st.integers(min_value=1, max_value=100000))
    event_type = draw(st.sampled_from(list(SessionEventType)))
    timestamp = draw(st.datetimes(timezones=st.just(timezone.utc)))
    payload = draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.booleans(), st.none()),
        max_size=10
    ))
    return SessionEvent(
        id=event_id,
        session_id=session_id,
        seq=seq,
        type=event_type,
        timestamp=timestamp,
        payload=payload
    )
```
