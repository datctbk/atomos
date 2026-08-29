# Unit 2 Functional Design Plan: LLM Adapter & Streaming Engine

## Purpose
Plan the detailed business logic, domain entities, message chunk models, SSE streaming protocol, and provider adapter interfaces for **Unit 2: LLM Adapter & Streaming Engine** (`python/atomos/llm/`).

---

## Execution Checklist

- [x] **Step 1: Collect User Functional Preferences for Unit 2** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 2 Domain Entities Document** (`aidlc-docs/construction/unit-2-llm-adapter/functional-design/domain-entities.md`)
- [x] **Step 4: Generate Unit 2 Business Logic Model** (`aidlc-docs/construction/unit-2-llm-adapter/functional-design/business-logic-model.md`)
- [x] **Step 5: Generate Unit 2 Business Rules & Validation** (`aidlc-docs/construction/unit-2-llm-adapter/functional-design/business-rules.md`)
- [ ] **Step 6: User Approval of Unit 2 Functional Design**

---

## Mandatory Artifacts to Generate
- `domain-entities.md`: Data models for `LLMMessage`, `LLMChunk`, `ToolCallChunk`, `UsageInfo`, `BaseLLMAdapter`, `DeepSeekAdapter`, and `OpenAIAdapter`.
- `business-logic-model.md`: SSE token chunk aggregation, incremental tool call reconstruction, and streaming lifecycle.
- `business-rules.md`: Chunk concatenation invariants, tool argument JSON fragment joining rules, and validation schemas.

---

## Functional Design Questions for Unit 2

Please answer the following questions to guide the design of the LLM streaming engine.

### Question 1: Incremental Tool Call Accumulation Protocol
How should fragmented tool call chunks streamed from the LLM (e.g. partial arguments like `{"fi`, `lename": "`, `test.py"}`) be represented and yielded?

A) **Unified Stream Yielding `LLMChunk` with both text and partial tool call deltas** (Recommended): Yields incremental `LLMChunk(delta_text, delta_tool_calls)`, with an in-flight accumulator reconstructing complete tool call objects when stream finishes

B) **Separate Token and Tool Call Event Channels**: Emit token chunks on one event stream and tool invocations only when fully completed

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Provider Factory & Model Selection Interface
How should provider adapters (DeepSeek, OpenAI, etc.) be selected and configured on the `Context`?

A) **Adapter Registration via `Context.provide("llm", adapter)` with Factory Helper**: A `create_llm_adapter(provider="deepseek", model="deepseek-chat")` factory registering the adapter on `Context` (recommended for DI flexibility)

B) **Global Configuration Object**: A static `LLMConfig` singleton read directly by adapters

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Token Usage & Finish Reason Propagation
How should token usage statistics (`prompt_tokens`, `completion_tokens`) and `finish_reason` be delivered?

A) **Delivered in the Final `LLMChunk`**: The last yielded `LLMChunk` has `finish_reason="stop" | "tool_calls"` and populated `usage` model (standard OpenAI/DeepSeek SSE convention)

B) **Emitted as a Dedicated Post-Stream Metadata Event**: `ctx.emit("llm/usage", usage)`

X) Other (please describe after [Answer]: tag below)

[Answer]: A
