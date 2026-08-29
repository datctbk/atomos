# Unit 2 Tech Stack Decisions: LLM Adapter & Streaming Engine

This document records the technology selections and networking client choices for Unit 2.

---

## 1. Technology Choices & Libraries

| Capability | Selected Library | Version | Rationale |
|---|---|---|---|
| **Async HTTP Client** | `httpx` | `>=0.27.0` | Standard async HTTP client with built-in SSE streaming response support (`client.stream()`) and granular timeouts. |
| **Local LLM Compatibility** | OpenAI-Compatible SSE Standard | HTTP/JSON SSE | Universal support across local runners (Ollama, LMStudio, vLLM, llama.cpp server) and cloud providers. |
| **Data Validation** | `pydantic` | `>=2.6.0` | High-performance serialization and schema validation for chat messages and tool fragments. |
| **Test Mocking** | `pytest-asyncio` + `MockLLMAdapter` | `>=0.23.0` | 100% offline reproducible test execution. |

---

## 2. Directory & Packaging Specifications
- **Package Path**: `python/atomos/llm/`
  - `python/atomos/llm/base.py`: Message models, chunks, and abstract adapter base.
  - `python/atomos/llm/providers/deepseek.py`: DeepSeek SSE client.
  - `python/atomos/llm/providers/openai.py`: OpenAI and Local LLM (Ollama/LMStudio/vLLM) SSE client.
  - `python/atomos/llm/mock.py`: Deterministic test mock adapter.
