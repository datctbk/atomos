# Unit 2 NFR Design Plan: LLM Adapter & Streaming Engine

## Purpose
Design the architectural patterns, full jitter backoff retry decorators (`RES-01`), local model endpoint connectors, and logical components for **Unit 2: LLM Adapter & Streaming Engine** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Design Preferences for Unit 2** (Completed with user answers: A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 2 NFR Design Patterns Document** (`aidlc-docs/construction/unit-2-llm-adapter/nfr-design/nfr-design-patterns.md`)
- [x] **Step 4: Generate Unit 2 Logical Components Document** (`aidlc-docs/construction/unit-2-llm-adapter/nfr-design/logical-components.md`)
- [ ] **Step 5: User Approval of Unit 2 NFR Design**

---

## Mandatory Artifacts to Generate
- `nfr-design-patterns.md`: Full jitter exponential backoff retry pattern (`RES-01`), SSE line buffer parser, and local Ollama/LMStudio endpoint routing.
- `logical-components.md`: Logical component specifications for `AsyncRetryRunner`, `SSEChunkStreamParser`, `LocalOpenAIAdapter`, and `MockLLMAdapter`.

---

## NFR Design Questions for Unit 2

Please answer the following questions to guide the non-functional design of the LLM subsystem.

### Question 1: Local Model Runner Adapter Hierarchy
How should the local LLM runner (Ollama, LMStudio, vLLM) be architected relative to the cloud OpenAI adapter?

A) **Unified `OpenAIAdapter` with `is_local` / `base_url` presets** (Recommended: A single, battle-tested OpenAI-compatible SSE client that defaults to `http://localhost:11434/v1` when configured for local execution without requiring dummy API keys)

B) **Separate Subclasses (`OllamaAdapter`, `LocalModelAdapter`)**: Dedicated subclass for each local tool runtime

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Retry with Full Jitter Integration Approach
How should the retry policy (`RES-01`) be wrapped around streaming requests?

A) **Async Generator Retry Wrapper (`retry_async_stream`)**: Transparently intercepts connection failures on initial handshake and mid-stream disconnects, executing backoff with jitter and resuming request (recommended)

B) **HTTPX Transport Event Hook**: Custom transport middleware attached to HTTP client pool

X) Other (please describe after [Answer]: tag below)

[Answer]: A
