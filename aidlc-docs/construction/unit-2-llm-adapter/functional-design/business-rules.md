# Unit 2 Business Rules & Validation: LLM Adapter & Streaming Engine

This document defines the invariants, business rules, validation constraints, and retry policies for Unit 2.

---

## 1. Core Invariants & Business Rules

### BR-LLM-01: Lossless Stream Aggregation
- **Rule**: Concatenating all `delta_content` strings yielded across a single streaming request MUST equal the final completed message content.
- **Verification**: Tested via property tests comparing non-streaming reference responses against concatenated chunk outputs.

### BR-LLM-02: Valid JSON Tool Call Arguments
- **Rule**: When `finish_reason == "tool_calls"`, the concatenated `arguments` string for every accumulated tool call MUST parse as valid JSON.
- **Validation**: If parsing fails due to model truncation, raise a structured `MalformedToolCallError` rather than crashing the turn loop.

### BR-LLM-03: Zero Hardcoded Credentials (SECURITY-07)
- **Rule**: Adapters MUST resolve API keys dynamically from environment variables (`DEEPSEEK_API_KEY`, `OPENAI_API_KEY`) or explicit constructor parameters.
- **Validation**: Raising `ConfigurationError` when no API key is available.

---

## 2. Testable Properties for Property-Based Testing (PBT-01)

| Property Name | Category | Description |
|---|---|---|
| `prop_tool_fragment_accumulation` | **Accumulator Invariant** | For any arbitrary partitioning of a JSON string into $k$ random chunks, `ToolCallAccumulator` reassembles the exact original string. |
| `prop_llm_message_serialization` | **Round-trip** | For all valid `LLMMessage` objects $m$, `LLMMessage.model_validate(m.model_dump()) == m`. |
