# Application Design Plan

## Purpose
Define the high-level system architecture, component boundaries, service layer orchestration, and interface contracts for the Python reimplementation of DeepSeek Harness (`dsh`).

---

## Execution Checklist

- [x] **Step 1: Collect User Design Preferences** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Components Document** (`aidlc-docs/inception/application-design/components.md`)
- [x] **Step 4: Generate Component Methods & Interface Contracts** (`aidlc-docs/inception/application-design/component-methods.md`)
- [x] **Step 5: Generate Services & Orchestration Patterns** (`aidlc-docs/inception/application-design/services.md`)
- [x] **Step 6: Generate Component Dependency & Data Flow** (`aidlc-docs/inception/application-design/component-dependency.md`)
- [x] **Step 7: Generate Consolidated Application Design** (`aidlc-docs/inception/application-design/application-design.md`)
- [ ] **Step 8: Present Design for User Review & Approval**

---

## Mandatory Design Artifacts
- `components.md`: Component responsibilities, boundaries, and public interfaces.
- `component-methods.md`: Method signatures, typed arguments, and return models.
- `services.md`: Service orchestration, dependency injection container, and turn flow.
- `component-dependency.md`: Dependency matrix and sequence diagrams.
- `application-design.md`: Consolidated master design document.

---

## Design Configuration Questions

Please answer the following questions to guide the architecture and interface designs.

### Question 1: Python Cordis Context & Dependency Injection Pattern
How should the Cordis dependency injection and plugin lifecycle container be implemented in Python?

A) **Class-Based Context with Scoped Service Registry**: A typed `Context` class where plugins inherit from `Plugin`, bind services via `ctx.provide(name, service)`, and register listeners with `ctx.on(event, handler)` with automatic unbind tokens (recommended, idiomatic Python Cordis equivalent)

B) **Protocol & Decorator-Driven IoC**: Using Python `@plugin`, `@service`, and `@hook` decorators with runtime dependency injection

C) **Lightweight Registry Dict**: Simple dictionary-based lookup for services and event listener lists

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: LLM Provider Client Architecture
How should the LLM integration layer be structured across different model providers?

A) **Unified Provider Adapter with Streaming Generator**: An abstract base class `BaseLLMAdapter` returning async iterators of `LLMChunk`, with concrete implementations for `DeepSeekAdapter` and `OpenAIAdapter`

B) **Direct HTTP Client via HTTPX**: Single configurable client targeting OpenAI-compatible streaming endpoints directly

C) **Multi-Provider Router**: Dynamic routing layer selecting backends with automatic failover and load balancing

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Tool Parameter Validation & Registration Model
How should tools define and validate their parameter schemas?

A) **Pydantic Model Base**: Tools subclass `BaseTool[TParams]` using Pydantic `BaseModel` for automatic JSON schema generation, type coercion, and security validation (recommended)

B) **Pure Python TypedDict / Type Hints**: Tools use standard function signatures with type hints and runtime `inspect`

C) **Raw JSON Schema**: Tools declare explicit JSON schema dictionaries

X) Other (please describe after [Answer]: tag below)

[Answer]: A
