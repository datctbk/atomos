# Unit 1 Code Generation Plan: Core Kernel & Event Sourcing Store

## 1. Unit Context & Traceability

- **Unit Name**: `unit-1-core-kernel`
- **Target Package Path**: `python/atomos/core/`
- **Target Test Path**: `python/tests/`
- **Mapped User Stories**: `US-03` (Durable Session History & Recovery), `US-05` (Custom Plugin & Tool Registration - Context part), `US-06` (Security & Resiliency Hardening - logging & persistence part)
- **Mapped Requirements**: `FR-01.1`, `FR-01.2`, `FR-01.3`, `FR-02.1`, `FR-02.2`, `FR-02.3`, `NFR-SEC-01`, `NFR-SEC-03`, `NFR-RES-01`, `NFR-PBT-01`, `NFR-PBT-02`

---

## 2. Step-by-Step Implementation Sequence

### Step 1: Project Setup & Package Manifest
- [x] Create `python/pyproject.toml` with PEP 621 packaging metadata, dependencies (`pydantic>=2.6.0`, `hypothesis>=6.100.0`, `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `ruff>=0.3.0`, `mypy>=1.9.0`), and tool configurations.
- [x] Create `python/atomos/__init__.py` exposing package version and top-level exports.
- [x] Create `python/atomos/core/__init__.py` exposing `Context`, `Disposable`, `EventBus`, `Session`, `SessionStore`, and `SessionEvent`.

### Step 2: Implement Dependency Injection Context (`context.py`)
- [x] Create `python/atomos/core/context.py` implementing:
  - `Disposable` protocol with `dispose()` callback.
  - `Context` class supporting `provide(name, service)`, `get(name, default)`, `on(event, handler)`, `waterfall(event, handler)`, `emit(event, *args, **kwargs)`, and `pipe(event, initial_value)`.
  - Scoped resource registration and lifecycle unbinding.

### Step 3: Implement EventBus & Waterfall Pipeline Engine (`events.py`)
- [x] Create `python/atomos/core/events.py` implementing:
  - Asynchronous broadcast event dispatching with sequential execution order.
  - Recursive `await next()` middleware chaining for waterfall interceptors.

### Step 4: Implement SessionEvent & Atomic SessionStore (`session.py`)
- [x] Create `python/atomos/core/session.py` implementing:
  - `SessionEventType` enum (`turn/start`, `user/message`, `assistant/chunk`, `assistant/message`, `tool/call`, `tool/result`, `turn/end`).
  - Immutable `SessionEvent` Pydantic model (`frozen=True`) with UTC timestamps, sequence numbers, and JSON serialization.
  - `AtomicEventWriter` line-buffered append persistence with `0o700`/`0o600` permissions (`SECURITY-01`) and `os.fsync()` durability (`RES-03`).
  - `Session` and `SessionStore` supporting session creation, event appending, and `.jsonl` session recovery.

### Step 5: Implement Logging & Redaction Filter (`logging.py`)
- [x] Create `python/atomos/core/logging.py` implementing:
  - `RedactionFilter` (`logging.Filter`) masking API keys (`sk-...`), bearer tokens, and secrets with `***MASKED***` (`SECURITY-03`).
  - Structured logger configuration with ISO timestamps and log levels.

### Step 6: Implement Unit Tests & Property-Based Test Suite
- [x] Create `python/tests/unit/test_context.py` testing service provision, lookup, unbinding, and scoping.
- [x] Create `python/tests/unit/test_events.py` testing broadcast events and waterfall pipeline rewrites.
- [x] Create `python/tests/unit/test_session.py` testing session creation, event appending, JSONL persistence, and recovery.
- [x] Create `python/tests/property/test_session_pbt.py` using `hypothesis` testing:
  - `prop_session_event_roundtrip`: `SessionEvent.model_validate_json(e.model_dump_json()) == e` (`PBT-01`).
  - `prop_session_seq_monotonic`: Sequence numbers strictly increment $1 \dots N$ (`PBT-02`).

### Step 7: Run Verification Tests & Generate Documentation Summary
- [x] Run `pytest` and `hypothesis` test suite to verify 100% pass rate.
- [x] Create `aidlc-docs/construction/unit-1-core-kernel/code/code-summary.md` documenting implementation details, test results, and compliance.
