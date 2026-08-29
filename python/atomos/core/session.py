"""Session and Event Sourcing models for Atomos."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from atomos.core.context import Context


class SessionEventType(str, Enum):
    """Classification types for session events."""

    TURN_START = "turn/start"
    USER_MESSAGE = "user/message"
    ASSISTANT_CHUNK = "assistant/chunk"
    ASSISTANT_MESSAGE = "assistant/message"
    TOOL_CALL = "tool/call"
    TOOL_RESULT = "tool/result"
    AGENT_INTERRUPT = "agent/interrupt"
    TURN_END = "turn/end"


class SessionEvent(BaseModel):
    """Immutable event representing a discreet interaction step."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    session_id: str
    seq: int
    type: SessionEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = Field(default_factory=dict)


class AtomicEventWriter:
    """Manages atomic, append-only JSONL event persistence with OS fsync (RES-03, SECURITY-01)."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        # Ensure parent directory exists with 0o700 permissions (SECURITY-01)
        self.file_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Open file with mode 0o600 (owner read/write only)
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        self._fd = os.open(str(self.file_path), flags, 0o600)
        self._file = open(self._fd, "w", encoding="utf-8", buffering=1)  # noqa: SIM115

    def append_line(self, line: str) -> None:
        """Write single JSON line and flush/fsync to disk."""
        self._file.write(line + "\n")
        self._file.flush()
        os.fsync(self._fd)

    def close(self) -> None:
        """Close underlying file descriptor."""
        if not self._file.closed:
            self._file.close()


class Session:
    """Represents an active or recovered agent session with append-only event history."""

    def __init__(
        self,
        session_id: str,
        storage_path: Path,
        ctx: Context | None = None,
    ) -> None:
        self.session_id = session_id
        self.storage_path = storage_path
        self.ctx = ctx
        self._events: list[SessionEvent] = []
        self._writer: AtomicEventWriter | None = None

    @property
    def events(self) -> list[SessionEvent]:
        """Return a copy of all recorded events."""
        return list(self._events)

    def get_next_seq(self) -> int:
        """Return the next monotonic sequence number."""
        return len(self._events) + 1

    def append_event(
        self,
        event_type: SessionEventType,
        payload: dict[str, Any] | None = None,
    ) -> SessionEvent:
        """Construct, record, persist, and broadcast a new session event."""
        if self._writer is None:
            self._writer = AtomicEventWriter(self.storage_path)

        seq = self.get_next_seq()
        event = SessionEvent(
            session_id=self.session_id,
            seq=seq,
            type=event_type,
            payload=payload or {},
        )
        self._events.append(event)
        self._writer.append_line(event.model_dump_json())

        if self.ctx is not None:
            # Emit asynchronous event broadcast non-blockingly for observers
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.ctx.emit("session/event", event))
            except RuntimeError:
                pass

        return event

    def load_history(self) -> list[SessionEvent]:
        """Read and validate all events from disk."""
        if not self.storage_path.exists():
            return []

        loaded: list[SessionEvent] = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    event = SessionEvent.model_validate_json(stripped)
                    loaded.append(event)

        self._events = loaded
        return list(self._events)

    def close(self) -> None:
        """Close persistence writer."""
        if self._writer is not None:
            self._writer.close()
            self._writer = None


class SessionStore:
    """Factory and repository for creating and retrieving persistent Sessions."""

    def __init__(self, base_dir: Path | None = None, ctx: Context | None = None) -> None:
        if base_dir is None:
            home = os.environ.get("ATOMOS_HOME")
            if home:
                base_dir = Path(home) / "sessions"
            else:
                base_dir = Path.home() / ".atomos" / "sessions"
        self.base_dir = base_dir
        self.ctx = ctx
        self._sessions: dict[str, Session] = {}

    def get_session_path(self, session_id: str) -> Path:
        """Derive the JSONL storage path for a session ID."""
        return self.base_dir / f"{session_id}.jsonl"

    def create_session(self, session_id: str | None = None) -> Session:
        """Create and register a new active session."""
        sid = session_id or uuid.uuid4().hex
        storage_path = self.get_session_path(sid)
        session = Session(session_id=sid, storage_path=storage_path, ctx=self.ctx)
        self._sessions[sid] = session
        return session

    def get_or_load_session(self, session_id: str) -> Session:
        """Retrieve existing in-memory session or load from disk."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        storage_path = self.get_session_path(session_id)
        session = Session(session_id=session_id, storage_path=storage_path, ctx=self.ctx)
        if storage_path.exists():
            session.load_history()
        self._sessions[session_id] = session
        return session

    def list_sessions(self) -> list[str]:
        """List all available session IDs found in the storage directory."""
        if not self.base_dir.exists():
            return []
        return [f.stem for f in self.base_dir.glob("*.jsonl")]
