# Unit 2 NFR Requirements: LLM Adapter & Streaming Engine

This document specifies the non-functional requirements, resilience baselines (`RES-01`), timeouts, and local LLM runtime specifications for Unit 2.

---

## 1. Local & Cloud LLM Provider Specifications

### NFR-LLM-01: Local LLM Execution Support
- **Requirement**: Support local offline LLM runners (Ollama, LMStudio, vLLM, llama.cpp server) implementing the OpenAI-compatible `/v1/chat/completions` protocol without requiring internet access or paid API keys.
- **Default Local Endpoint**: `http://localhost:11434/v1` (Ollama) or configurable via `ATOMOS_LOCAL_LLM_URL` / `base_url`.
- **Default Local Model**: Configurable (e.g. `deepseek-r1`, `qwen2.5-coder`, `llama3`).

### NFR-LLM-02: Cloud Provider Support
- **Providers**: DeepSeek (`https://api.deepseek.com/v1`), OpenAI (`https://api.openai.com/v1`), OpenRouter (`https://openrouter.ai/api/v1`).
- **Authentication**: Token resolution from environment variables (`DEEPSEEK_API_KEY`, `OPENAI_API_KEY`) (`SECURITY-07`).

---

## 2. Performance & Streaming Latency

### NFR-PERF-01: Time-To-First-Token (TTFT)
- **Target**: Initial chunk emitted to caller $< 100\text{ms}$ after receipt of the first SSE line from the HTTP socket.
- **Target**: Memory overhead $< 1\text{MB}$ per streaming request using generator stream iteration.

### NFR-PERF-02: Granular Network Timeouts
- **Connect Timeout**: 10.0 seconds
- **Read / Stream Inactivity Timeout**: 60.0 seconds
- **Write Timeout**: 10.0 seconds
- **Connection Pool Timeout**: 10.0 seconds

---

## 3. Resiliency & Fault Tolerance (RES-01)

### NFR-RES-01: Exponential Backoff with Full Jitter
- **Retry Conditions**: HTTP 429 (Rate Limit), HTTP 502/503/504 (Server Errors), Network connection resets (`httpx.ConnectError`, `httpx.RemoteProtocolError`).
- **Algorithm**: Full Jitter Backoff
  $$\text{delay} = \text{random}(0, \min(\text{max\_delay}, \text{base\_delay} \cdot 2^{\text{attempt}}))$$
- **Parameters**: Max retries = 3, Base delay = 1.0s, Max delay = 10.0s.

---

## 4. Testability & Offline Mocking

### NFR-TEST-01: Deterministic Offline Test Mocking
- **Requirement**: Provide `MockLLMAdapter` yielding deterministic canned token streams and simulated tool calls for offline CI/CD and property testing without API network access.
