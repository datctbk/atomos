# Unit 1 NFR Requirements: Core Kernel & Event Sourcing Store

This document specifies the non-functional requirements, performance thresholds, security baselines, and quality metrics for Unit 1.

---

## 1. Performance & Latency Requirements

### NFR-PERF-01: Low-Latency Event Append
- **Target**: `Session.append_event()` must complete in `< 2ms` per event under normal load.
- **Implementation**: Append-only file mode (`'a'`) with line buffering and standard file descriptor flush.

### NFR-PERF-02: Micro-Kernel DI Overhead
- **Target**: `Context.get()` lookup latency must be $< 50\mu s$ (pure dictionary lookup).
- **Target**: Event dispatch overhead (`ctx.emit`) must be $< 100\mu s$ per registered listener.

---

## 2. Security Requirements (Enforcing Security Baseline)

### NFR-SEC-01: Session File Storage Security (SECURITY-01)
- **Rule**: Session directory `~/.atomos/sessions/` must be created with mode `0o700` (read/write/execute restricted to the current user).
- **Rule**: Individual `.jsonl` session files must be created with mode `0o600` (read/write by owner only).

### NFR-SEC-03: Structured Logging & Redaction (SECURITY-03)
- **Rule**: Structured logging via standard Python logging.
- **Rule**: Automatic redaction filter masking all sensitive tokens (`API_KEY`, `TOKEN`, `BEARER`).

---

## 3. Resiliency Requirements (Enforcing Resiliency Baseline)

### NFR-RES-01: Atomic Session Persistence (RES-03)
- **Rule**: Every event appended to `Session` must be flushed to the file descriptor immediately before the coroutine returns.
- **Rule**: Corrupted JSONL lines encountered during session recovery must raise descriptive validation errors without crashing unrelated sessions.

---

## 4. Property-Based Testing Requirements (Enforcing PBT Baseline)

### NFR-PBT-01: Round-Trip Serialization Invariant (PBT-01)
- **Property**: For all generated `SessionEvent` instances $e$, `SessionEvent.model_validate_json(e.model_dump_json()) == e`.
- **Framework**: `hypothesis` property test runner with composite generators for nested payloads and timestamps.

### NFR-PBT-02: Monotonic Sequence Invariant (PBT-02)
- **Property**: Appending $N$ random events to a `Session` must produce sequence numbers $[1, 2, \dots, N]$.
