# Component Methods & Interface Contracts

This document specifies the method signatures, typed inputs, outputs, and interface protocols across all core components.

---

## 1. Context & EventBus Interfaces (`dsh.core.context`, `dsh.core.events`)

```python
from typing import Any, AsyncIterator, Callable, Coroutine, Protocol, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")

class Disposable(Protocol):
    def dispose(self) -> None: ...

class Context:
    """Cordis-equivalent Dependency Injection & Plugin lifecycle container."""
    def provide(self, name: str, service: Any) -> Disposable:
        """Registers a service under a designated key name."""
        ...

    def get(self, name: str, default: Any = None) -> Any:
        """Retrieves a registered service instance."""
        ...

    def on(self, event: str, handler: Callable[..., Coroutine[Any, Any, None]]) -> Disposable:
        """Registers an asynchronous event listener with auto-unbind token."""
        ...

    def waterfall(self, event: str, handler: Callable[[Any, Callable[[], Coroutine[Any, Any, Any]]], Coroutine[Any, Any, Any]]) -> Disposable:
        """Registers a waterfall middleware interceptor invoking await next()."""
        ...

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Dispatches an asynchronous broadcast event to all registered listeners."""
        ...

    async def pipe(self, event: str, initial_value: Any) -> Any:
        """Executes a waterfall pipeline passing transformed data through each handler."""
        ...
```

---

## 2. Session & Event Store Interfaces (`dsh.core.session`)

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class SessionEventType(str, Enum):
    TURN_START = "turn/start"
    USER_MESSAGE = "user/message"
    ASSISTANT_CHUNK = "assistant/chunk"
    ASSISTANT_MESSAGE = "assistant/message"
    TOOL_CALL = "tool/call"
    TOOL_RESULT = "tool/result"
    TURN_END = "turn/end"

class SessionEvent(BaseModel):
    id: str = Field(..., description="Unique event identifier (UUID)")
    session_id: str = Field(..., description="Parent session identifier")
    seq: int = Field(..., description="Monotonically increasing sequence number")
    type: SessionEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any] = Field(default_factory=dict)

class SessionStore:
    def create_session(self, session_id: str | None = None) -> Session:
        """Creates a new session and initializes storage."""
        ...

    def get_session(self, session_id: str) -> Session | None:
        """Retrieves an existing session instance."""
        ...

class Session:
    session_id: str
    events: list[SessionEvent]

    async def append_event(self, event_type: SessionEventType, payload: dict[str, Any]) -> SessionEvent:
        """Appends a new event to memory and atomic JSONL file persistence."""
        ...

    def get_history(self) -> list[SessionEvent]:
        """Returns the complete immutable event history for this session."""
        ...
```

---

## 3. LLM Adapter & Streaming Engine (`dsh.llm`)

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Literal

class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None

class LLMChunk(BaseModel):
    delta_content: str = ""
    delta_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    finish_reason: str | None = None
    usage: dict[str, int] | None = None

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> AsyncIterator[LLMChunk]:
        """Streams completion chunks from the model provider."""
        ...
```

---

## 4. Scoped Tool Registry Interfaces (`dsh.tools`)

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

TParams = TypeVar("TParams", bound=BaseModel)

class ToolContext(BaseModel):
    session_id: str
    workspace_root: str
    caller_id: str | None = None

class ToolResult(BaseModel):
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class BaseTool(ABC, Generic[TParams]):
    name: str
    description: str
    param_schema: type[TParams]

    @abstractmethod
    async def execute(self, params: TParams, context: ToolContext) -> ToolResult:
        """Executes the tool with validated Pydantic parameters."""
        ...

    def get_json_schema(self) -> dict[str, Any]:
        """Returns OpenAI-compatible JSON Schema for model tool definitions."""
        ...

class ToolRegistry:
    def register_tool(self, tool: BaseTool[Any]) -> Disposable:
        """Registers a tool in the active context."""
        ...

    async def execute_tool(
        self, name: str, raw_arguments: dict[str, Any] | str, context: ToolContext
    ) -> ToolResult:
        """Validates arguments, executes pre/post interceptors, and runs the tool."""
        ...
```

---

## 5. Agent Loop & Turn Orchestrator (`dsh.core.agent_loop`)

```python
class TurnResult(BaseModel):
    session_id: str
    turn_id: str
    status: Literal["completed", "stopped", "error"]
    steps_taken: int
    final_message: str | None = None
    error_message: str | None = None

class AgentLoop:
    async def start_turn(self, session: Session, user_prompt: str) -> TurnResult:
        """Orchestrates turn claiming, prompt compilation, streaming, tool executions, and turn closure."""
        ...

    async def stop_turn(self, session_id: str, reason: str = "user_interrupted") -> None:
        """Signals active step and turn to cleanly terminate."""
        ...
```
