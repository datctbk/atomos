# Unit 1 Functional Design Plan: Core Kernel & Event Sourcing Store

## Purpose
Plan the detailed business logic, domain models, entity relationships, and validation rules for **Unit 1: Core Kernel & Event Sourcing Store** (`python/dsh/core/context.py`, `events.py`, `session.py`).

---

## Execution Checklist

- [x] **Step 1: Collect User Functional Preferences for Unit 1** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Domain Entities Document** (`aidlc-docs/construction/unit-1-core-kernel/functional-design/domain-entities.md`)
- [x] **Step 4: Generate Business Logic Model** (`aidlc-docs/construction/unit-1-core-kernel/functional-design/business-logic-model.md`)
- [x] **Step 5: Generate Business Rules & Validation** (`aidlc-docs/construction/unit-1-core-kernel/functional-design/business-rules.md`)
- [ ] **Step 6: User Approval of Unit 1 Functional Design**

---

## Mandatory Artifacts to Generate
- `domain-entities.md`: Data models for `SessionEvent`, `Session`, `Context`, `Disposable`, `EventSubscription`.
- `business-logic-model.md`: Event append-only lifecycle, waterfall handler execution rules, and plugin lifecycle unbinding flows.
- `business-rules.md`: Monotonic sequence ordering rules, event type validations, and error handling policies.

---

## Functional Design Questions for Unit 1

Please answer the following questions to guide the detailed logic design for Unit 1.

### Question 1: Event Bus Concurrency & Execution Ordering
How should broadcast and waterfall event listeners be executed when multiple handlers are registered?

A) **Sequential Async Execution**: Broadcast listeners execute in registered order one after another with `await`, and waterfall interceptors chain via explicit `await next()` (recommended for deterministic replay and state consistency)

B) **Concurrent Async Gathering**: Broadcast listeners execute in parallel using `asyncio.gather()`, while waterfalls remain serial

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Session Event Persistence Strategy
How should session events be persisted to disk during an active turn?

A) **Immediate Append-and-Flush**: Each `append_event()` call atomically writes the JSON string line to `~/.dsh/sessions/{session_id}.jsonl` and flushes to disk immediately (ensures zero data loss on abrupt termination)

B) **Turn-Boundary Buffered Flush**: Events are buffered in memory and flushed in batch at `turn/end`

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Context Disposable Cleanup Handling
What behavior should occur if a plugin or service registration is disposed while async handlers are actively running?

A) **Graceful Token Unbinding**: Disposing a registration immediately removes it from active registry lookup while allowing currently in-flight coroutines to finish cleanly (recommended)

B) **Strict Hard Cancellation**: Disposing cancels active in-flight coroutines tied to that plugin scope

X) Other (please describe after [Answer]: tag below)

[Answer]: A
