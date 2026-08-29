# Unit 1 Tech Stack Decisions: Core Kernel & Event Sourcing Store

This document records the technology and library selections for Unit 1.

---

## 1. Technology Choices & Libraries

| Capability | Selected Library | Version | Rationale |
|---|---|---|---|
| **Runtime Language** | Python | `>=3.11` | Modern `asyncio`, type hints, `Protocol`, and high performance. |
| **Data Validation & Schemas** | `pydantic` | `>=2.6.0` | Ultra-fast Rust-backed validation and JSON serialization. |
| **Testing Framework** | `pytest` + `pytest-asyncio` | `>=8.0.0` | Industry standard async unit testing. |
| **Property-Based Testing** | `hypothesis` | `>=6.100.0` | Advanced automated invariant testing with shrinking counterexamples. |
| **Formatting & Linting** | `ruff` | `>=0.3.0` | Extremely fast Python linter and formatter. |
| **Static Type Checking** | `mypy` | `>=1.9.0` | Strict static type checking (`strict = true`). |

---

## 2. Directory & Packaging Specifications
- **Root Directory**: `python/`
- **Package Path**: `python/atomos/core/`
- **Dependencies Specification**: Standard `pyproject.toml` (PEP 518/621 compliant).
