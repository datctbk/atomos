# Unit 4 Business Rules & Validation: Agent Loop & Turn Driver

This document specifies the invariants, guardrail rules, max iteration thresholds, and property testing invariants for Unit 4.

---

## 1. Core Invariants & Business Rules

### BR-LOOP-01: Guaranteed Sequential Event Durability
- **Rule**: Every user input, assistant chunk generation, tool call, and tool result MUST be persisted as an immutable `SessionEvent` with monotonic sequence numbers before next action starts.
- **Verification**: Complete turn execution can be perfectly reconstructed from `session.events`.

### BR-LOOP-02: Infinite Loop Guardrail
- **Rule**: The agent loop MUST NOT exceed `max_iterations = 25` tool calling loops per user turn.
- **Action**: When `iteration == max_iterations`, execution halts immediately, yielding a graceful summary notification.

### BR-LOOP-03: System Prompt Invariance
- **Rule**: Context window compaction MUST always preserve the initial `system_prompt` at index 0 regardless of how many message turns are pruned.

### BR-LOOP-04: Non-Blocking Event Broadcasting
- **Rule**: State transitions (`agent/turn_start`, `agent/token`, `agent/tool_start`, `agent/tool_end`, `agent/turn_end`) MUST be non-blockingly broadcast to the `Context` event bus to allow middleware and observers to hook into the turn lifecycle.

---

## 2. Testable Properties for Property-Based Testing (PBT-01)

| Property Name | Category | Description |
|---|---|---|
| `prop_context_compaction_invariants` | **State Invariant** | For any arbitrary list of $M$ messages compacted with budget $N < M$, result always starts with `system` message (if present) and contains $\le N + 1$ total messages. |
| `prop_agent_loop_monotonic_events` | **Event Sourcing** | For multi-turn agent runs with simulated tool iterations, sequence IDs in session events strictly monotonically increase without gaps. |
