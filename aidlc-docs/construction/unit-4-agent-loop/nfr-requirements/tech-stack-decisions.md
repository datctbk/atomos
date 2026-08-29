# Unit 4 Tech Stack Decisions: Agent Loop & Turn Driver

This document records the technology selections and async streaming architectures for Unit 4.

---

## 1. Technology Choices & Libraries

| Capability | Selected Approach | Version | Rationale |
|---|---|---|---|
| **Turn Driver Generator** | Native Async Generators (`AsyncIterator[str]`) | Python 3.12 | Zero-overhead streaming to CLI/SDK callers with direct cancellation propagation. |
| **Data Validation & State** | `pydantic` | `>=2.6.0` | Strict data modeling for `TurnOptions`, `AgentStatus`, and `UsageInfo`. |
| **Testing & Invariant Verification** | `hypothesis` + `pytest-asyncio` | `>=6.100.0` | High-iteration property fuzzing for context compaction and monotonic event streams. |

---

## 2. Directory & Packaging Specifications
- **Package Path**: `python/atomos/agent/`
  - `python/atomos/agent/loop.py`: `AgentLoop`, `TurnOptions`, `AgentStatus`, `ContextCompactor`.
  - `python/atomos/agent/__init__.py`: Public agent module namespace.
