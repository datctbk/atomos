# Unit 4 NFR Design Plan: Agent Loop & Turn Driver

## Purpose
Design the architectural patterns, state machine models, event bus broadcast pipelines, and streaming token forwarders for **Unit 4: Agent Loop & Turn Driver** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Design Preferences for Unit 4** (Completed with user answers: A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 4 NFR Design Patterns Document** (`aidlc-docs/construction/unit-4-agent-loop/nfr-design/nfr-design-patterns.md`)
- [x] **Step 4: Generate Unit 4 Logical Components Document** (`aidlc-docs/construction/unit-4-agent-loop/nfr-design/logical-components.md`)
- [ ] **Step 5: User Approval of Unit 4 NFR Design**

---

## Mandatory Artifacts to Generate
- `nfr-design-patterns.md`: Streaming token generator pattern, Context event bus hooks, and Context compactor algorithm.
- `logical-components.md`: Logical component specifications for `AgentLoop`, `ContextCompactor`, `TurnMetricsTracker`, and `AgentStateBroadcast`.

---

## NFR Design Questions for Unit 4

Please answer the following questions to guide the non-functional design of the agent turn driver.

### Question 1: Turn Cancellation & Interrupt Handling
How should in-flight LLM streams and tool operations be cancelled when interrupted (e.g. user pressing Ctrl+C or abort signal)?

A) **Asyncio Task Cancellation with Graceful State Flushed**: Cancelling the async generator cleanly closes the HTTP socket, stops active tool subprocesses, and appends a `TURN_CANCELLED` session event (recommended)

B) **Hard Termination without Session Persistence**: Immediately halts without recording cancellation event

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Event Broadcast Pipeline & Lifecycle Hooks
How should the turn driver broadcast streaming events to `Context`?

A) **Non-blocking Event Bus Notification (`ctx.emit`)**: Emits `agent/turn_start`, `agent/token`, `agent/tool_start`, `agent/tool_end`, and `agent/turn_end` events directly through the DI event bus without blocking streaming throughput (recommended)

B) **Callback Interface Subscription**: Requires passing a callback object to `run_turn`

X) Other (please describe after [Answer]: tag below)

[Answer]: A
