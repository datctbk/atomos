# Unit 1 Business Rules & Validation: Core Kernel & Event Sourcing Store

This document defines the invariants, business rules, validation constraints, and error handling policies for Unit 1.

---

## 1. Core Invariants & Business Rules

### BR-01: Monotonic Event Sequence
- **Rule**: Every `SessionEvent` recorded within a session MUST have a `seq` integer strictly equal to `preceding_seq + 1`, starting from `1`.
- **Validation**: On append and on session load from file, sequence continuity is asserted. Gaps or duplicate sequence numbers raise `SessionSequenceError`.

### BR-02: Immutability of Recorded Events
- **Rule**: Once appended to `Session.events`, a `SessionEvent` is frozen and must never be mutated or deleted in place.
- **Validation**: `SessionEvent` models are configured with Pydantic `frozen=True` or copy-on-read semantics.

### BR-03: Event Type Classification
- **Rule**: All events must belong to the valid `SessionEventType` enumeration:
  - `turn/start`: Signals turn initiation.
  - `user/message`: Represents incoming user prompt or injected context.
  - `assistant/chunk`: Streaming fragment of model token generation.
  - `assistant/message`: Final accumulated assistant message and tool calls.
  - `tool/call`: Tool call invocation request.
  - `tool/result`: Execution output or error returned from tool.
  - `turn/end`: Final turn closure.
- **Validation**: Rejects unrecognized event type strings at schema validation time.

### BR-04: Reversible Plugin Registration
- **Rule**: Any service or listener registered to `Context` MUST return a `Disposable` instance.
- **Behavior**: Calling `disposable.dispose()` removes only that specific registration from `Context` without affecting existing or concurrent handlers.

### BR-05: Atomic Persistence & Flush
- **Rule**: Every `append_event()` invocation MUST write and flush to the `.jsonl` stream immediately before returning.
- **Verification**: Zero data loss across process interruptions or crashes (`RES-03`).

---

## 2. Testable Properties for Property-Based Testing (PBT-01)

| Property Name | Category | Description |
|---|---|---|
| `prop_session_event_roundtrip` | **Round-trip** | For all valid `SessionEvent` objects `e`, `SessionEvent.model_validate_json(e.model_dump_json()) == e`. |
| `prop_session_seq_monotonic` | **Invariant** | For any list of appended events $[e_1, \dots, e_n]$, `[e.seq for e in events] == list(range(1, n + 1))`. |
| `prop_context_disposable_idempotent`| **Idempotence** | Calling `disposable.dispose()` multiple times produces identical state without exceptions. |
