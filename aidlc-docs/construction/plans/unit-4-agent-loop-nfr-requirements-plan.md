# Unit 4 NFR Requirements Plan: Agent Loop & Turn Driver

## Purpose
Assess and specify non-functional requirements, streaming latency targets, cumulative token accounting, and property-based test strategies for **Unit 4: Agent Loop & Turn Driver** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Preferences for Unit 4** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 4 NFR Requirements Document** (`aidlc-docs/construction/unit-4-agent-loop/nfr-requirements/nfr-requirements.md`)
- [x] **Step 4: Generate Unit 4 Tech Stack Decisions Document** (`aidlc-docs/construction/unit-4-agent-loop/nfr-requirements/tech-stack-decisions.md`)
- [ ] **Step 5: User Approval of Unit 4 NFR Requirements**

---

## Mandatory Artifacts to Generate
- `nfr-requirements.md`: Token streaming latency targets ($< 50\text{ms}$ dispatch overhead), cumulative usage accounting, session event persistence durability, and property invariants.
- `tech-stack-decisions.md`: Async generator pipelining and Pydantic models.

---

## NFR Planning Questions for Unit 4

Please answer the following questions to establish the non-functional specifications for Unit 4.

### Question 1: Cumulative Token Accounting Strategy
How should token usage across multi-iteration tool calls within a single user turn be aggregated?

A) **Cumulative Session & Turn Usage Tracker**: Maintains both per-turn aggregated token totals (prompt, completion, total) and overall cumulative session totals persisted in `SessionEvent` metadata (recommended)

B) **Last Step Usage Only**: Only records token counts from the final assistant chunk

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Real-Time Token Streaming Dispatch Latency
What latency overhead target should the AgentLoop enforce when forwarding chunks from the LLM adapter to the consumer?

A) **Immediate Zero-Buffer Yielding ($< 5\text{ms}$ Dispatch Overhead)**: Tokens are yielded to the caller generator immediately as received from the LLM SSE stream without intermediate batching (recommended)

B) **Micro-Batched Token Dispatching (50ms chunks)**: Batches tokens over 50ms intervals before yielding

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Property-Based Testing for Turn Driver Invariants (PBT-01)
What state properties should Hypothesis verify on the AgentLoop?

A) **Event Sourcing Invariance & Monotonic Sequence Numbering**: Generating arbitrary random sequences of tool calls, mock responses, and errors, verifying that event IDs, timestamps, and sequence numbers are strictly monotonic and gapless (recommended)

B) **Deterministic Scenario Tests**: Fixed multi-turn conversation scenarios

X) Other (please describe after [Answer]: tag below)

[Answer]: A
