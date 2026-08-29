# Unit 4 NFR Requirements: Agent Loop & Turn Driver

This document specifies the non-functional requirements, streaming latency targets, cumulative accounting policies, and property invariants for Unit 4.

---

## 1. Performance & Latency Budgets

### NFR-PERF-01: Zero-Buffer Token Dispatch Overhead
- **Target**: Internal dispatch latency from receiving an `LLMChunk` to yielding it to the consumer $< 5\text{ms}$.
- **Design**: Direct async generator yielding without intermediate batching delays.

### NFR-PERF-02: Context Compaction Overhead
- **Target**: Sliding window compaction latency $< 2\text{ms}$ for histories up to 1,000 messages.

---

## 2. Reliability & State Durability

### NFR-REL-01: Atomic Event Persistence
- **Rule**: Every intermediate state transition (`USER_MESSAGE`, `ASSISTANT_MESSAGE`, `TOOL_CALL`, `TOOL_RESULT`) is synchronously written and flushed via `Session` before starting the next async operation.

### NFR-REL-02: Cumulative Token Accounting
- **Rule**: Accurately tracks prompt, completion, and total tokens across all tool iterations in a turn and maintains session lifetime cumulative aggregates.

---

## 3. Property-Based Testing Requirements (PBT-01)

### NFR-PBT-01: Sequence Monotonicity Invariant
- **Property**: For all generated multi-turn executions with arbitrary tool iterations, `session.events` has strictly monotonic sequence IDs with $\text{seq}_{i+1} == \text{seq}_i + 1$.
