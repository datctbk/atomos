# Unit 4 Functional Design Plan: Agent Loop & Turn Driver

## Purpose
Plan the core agent loop state machine, multi-turn tool calling driver, prompt compaction/history windowing, and session event broadcasting for **Unit 4: Agent Loop & Turn Driver** (`python/atomos/agent/`).

---

## Execution Checklist

- [x] **Step 1: Collect User Functional Preferences for Unit 4** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 4 Domain Entities Document** (`aidlc-docs/construction/unit-4-agent-loop/functional-design/domain-entities.md`)
- [x] **Step 4: Generate Unit 4 Business Logic Model** (`aidlc-docs/construction/unit-4-agent-loop/functional-design/business-logic-model.md`)
- [x] **Step 5: Generate Unit 4 Business Rules & Validation** (`aidlc-docs/construction/unit-4-agent-loop/functional-design/business-rules.md`)
- [ ] **Step 6: User Approval of Unit 4 Functional Design**

---

## Mandatory Artifacts to Generate
- `domain-entities.md`: Data models for `AgentState`, `AgentStatus`, `TurnContext`, `AgentLoop`, and `CompactionStrategy`.
- `business-logic-model.md`: Turn execution lifecycle (User Input -> Context Assemble -> Stream Tokens -> Execute Tool Calls -> Loop until Stop or Max Iterations).
- `business-rules.md`: Max iterations limits, infinite loop guardrails, token budget management, and cancellation support.

---

## Functional Design Questions for Unit 4

Please answer the following questions to guide the design of the agent execution loop.

### Question 1: Tool Call Multi-Turn Execution Mode
How should the agent loop handle turns where the LLM requests multiple tool invocations in a single response?

A) **Sequential Execution with Cumulative Event Streaming**: Executes tool calls sequentially in the order requested, persisting a `TOOL_RESULT` event for each, and feeding all outputs back to the next LLM step (recommended for reliable side-effects)

B) **Parallel Async Execution (`asyncio.gather`)**: Executes independent tool calls concurrently

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Maximum Turn Iteration Limit & Infinite Loop Protection
What should be the default maximum tool iteration depth per user message before prompting or terminating?

A) **Configurable `max_iterations = 25` with Graceful Termination Event**: If the model exceeds 25 consecutive tool call loops without stopping, the loop terminates and emits a warning message (recommended)

B) **Uncapped Iteration Count**: Runs indefinitely until the model emits a stop reason

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Context Compaction Strategy for Long Conversations
How should message history exceeding the context window budget be pruned?

A) **Sliding Window Pruning (Keep System Prompt + Last N Messages with Summarization Marker)** (Recommended: Preserves system instructions and recent conversation context without overflowing token limits)

B) **FIFO Truncation**: Drops oldest messages first without preserving system prompt

X) Other (please describe after [Answer]: tag below)

[Answer]: A
