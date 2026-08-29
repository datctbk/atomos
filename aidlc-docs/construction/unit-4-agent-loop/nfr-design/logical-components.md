# Unit 4 Logical Components: Agent Loop & Turn Driver

This document specifies the logical component structure and interaction model for Unit 4.

---

## 1. Component Architecture Diagram

```mermaid
graph TD
    User["Caller / CLI / SDK"]
    Loop["AgentLoop<br/>(atomos.agent.loop)"]
    Compactor["ContextCompactor"]
    EventBus["EventBus / Context<br/>(atomos.core.events)"]
    Session["SessionStore / Session<br/>(atomos.core.session)"]
    LLM["BaseLLMAdapter<br/>(atomos.llm.base)"]
    Tools["ToolRegistry<br/>(atomos.tools.base)"]

    User -->|run_turn| Loop
    Loop -->|compact_history| Compactor
    Loop -->|emit events| EventBus
    Loop -->|append_event| Session
    Loop -->|stream| LLM
    Loop -->|execute_tool| Tools
    Loop -->|yield tokens| User
```

---

## 2. Logical Components Breakdown

### 2.1 `AgentLoop` (`atomos.agent.loop`)
- **Type**: Core Turn Driver
- **Responsibilities**:
  - Coordinates turn lifecycle, streaming token delivery, and tool calling iterations.
  - Automatically persists user, assistant, and tool result events to `Session`.
  - Dispatches non-blocking lifecycle events to `Context`.

### 2.2 `ContextCompactor` (`atomos.agent.loop`)
- **Type**: Context Strategy Component
- **Responsibilities**:
  - Converts stored session event payloads into LLM chat messages (`LLMMessage`).
  - Prunes excess messages using sliding window heuristics while preserving the system prompt.

### 2.3 `TurnOptions` (`atomos.agent.loop`)
- **Type**: Configuration Model
- **Responsibilities**:
  - Encapsulates execution parameters (`max_iterations`, `system_prompt`, `max_history_messages`).
