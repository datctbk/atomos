# Unit 5 NFR Requirements: Bundles, CLI & SDK

This document specifies the performance benchmarks, cold-start latency limits, terminal rendering resilience, and property invariants for Unit 5.

---

## 1. Performance & Latency Budgets

### NFR-PERF-01: CLI Cold-Start Latency
- **Target**: CLI initialization time for `atomos --help` $< 150\text{ms}$.
- **Design**: Deferred lazy importing of heavy network libraries (`httpx`) until a run command is actively executed.

### NFR-PERF-02: Live Terminal Rendering Throughput
- **Target**: Rich terminal output rendering overhead $< 10\text{ms}$ per chunk without blocking async event loops.

---

## 2. Terminal Environment Resilience

### NFR-RES-01: Headless / Non-TTY Auto Detection
- **Rule**: When terminal stdout is redirected or piped (`not sys.stdout.isatty()`), the CLI automatically disables Rich dynamic live elements and outputs clean raw token streams.

---

## 3. Property-Based Testing Requirements (PBT-01)

### NFR-PBT-01: SDK Context Cleanup
- **Property**: For all randomly generated configurations and execution turns, `async with AtomosClient(...)` guarantees 100% session finalization and context disposal upon context exit.
