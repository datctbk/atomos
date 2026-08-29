# Unit 2 Code Generation Plan: LLM Adapter & Streaming Engine

## 1. Unit Context & Traceability

- **Unit Name**: `unit-2-llm-adapter`
- **Target Package Path**: `python/atomos/llm/`
- **Target Test Path**: `python/tests/`
- **Mapped User Stories**: `US-01` (Interactive CLI Agent Session - LLM part), `US-04` (Programmatic SDK Turn Orchestration - LLM streaming part), `US-06` (Security & Resiliency Hardening - full jitter retry & credential protection)
- **Mapped Requirements**: `FR-04.1`, `FR-04.2`, `FR-04.3`, `NFR-LLM-01`, `NFR-LLM-02`, `NFR-PERF-01`, `NFR-PERF-02`, `NFR-RES-01`, `SECURITY-07`, `PBT-01`

---

## 2. Step-by-Step Implementation Sequence

### Step 1: Base Message Models, Chunks & Abstract Adapter (`base.py`)
- [x] Create `python/atomos/llm/base.py` implementing:
  - `LLMRole` (`system`, `user`, `assistant`, `tool`).
  - `LLMMessage`, `ToolCallFragment`, `UsageInfo`, and `LLMChunk` Pydantic models.
  - `ToolCallAccumulator` reconstructing fragmented streaming tool calls.
  - `BaseLLMAdapter` abstract base class with `stream(messages, tools)`.
- [x] Create `python/atomos/llm/__init__.py` exposing core LLM types and adapters.

### Step 2: Implement Resilience Retry with Full Jitter (`retry.py`)
- [x] Create `python/atomos/llm/retry.py` implementing:
  - `retry_async_stream` wrapping async generator calls with exponential backoff and random full jitter ($base \cdot 2^{attempt}$) (`RES-01`).

### Step 3: Implement Provider Adapters (Cloud DeepSeek & Cloud/Local OpenAI)
- [x] Create `python/atomos/llm/providers/__init__.py`.
- [x] Create `python/atomos/llm/providers/deepseek.py` implementing:
  - `DeepSeekAdapter` with SSE line parsing, authentication via `DEEPSEEK_API_KEY`, and custom endpoints (`SECURITY-07`).
- [x] Create `python/atomos/llm/providers/openai.py` implementing:
  - `OpenAIAdapter` with dual Cloud and Local execution mode (`is_local=True` defaulting to `http://localhost:11434/v1` for Ollama/LMStudio/vLLM).

### Step 4: Implement Test Mock Adapter (`mock.py`)
- [x] Create `python/atomos/llm/mock.py` implementing:
  - `MockLLMAdapter` simulating chunked streaming responses, simulated network latency, and multi-tool invocations for 100% offline unit/integration testing.

### Step 5: Implement Unit & Property-Based Test Suites
- [x] Create `python/tests/unit/test_llm_base.py` testing message models and `ToolCallAccumulator`.
- [x] Create `python/tests/unit/test_llm_retry.py` testing full jitter retry on transient errors (`RES-01`).
- [x] Create `python/tests/unit/test_llm_providers.py` testing DeepSeek, OpenAI cloud, and Local OpenAI streaming payloads.
- [x] Create `python/tests/property/test_llm_pbt.py` using `hypothesis` testing:
  - `prop_tool_fragment_accumulation`: Verifying arbitrary JSON chunk partitioning reassembly (`PBT-01`).

### Step 6: Run Verification Tests & Generate Documentation Summary
- [x] Run `pytest`, `hypothesis`, `ruff`, and `mypy` test suite to verify 100% pass rate.
- [x] Create `aidlc-docs/construction/unit-2-llm-adapter/code/code-summary.md` documenting implementation details, test results, and compliance.
