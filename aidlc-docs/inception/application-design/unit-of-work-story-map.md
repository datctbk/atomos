# Unit of Work to Story & Requirement Traceability Map

This document establishes bidirectional traceability between User Stories, Requirements, Extensions, and the 5 Construction Units.

---

## 1. Traceability Matrix

| User Story | Primary Unit | Mapped Functional Requirements | Enforced Extension Constraints |
|---|---|---|---|
| **US-01**: Interactive CLI Agent Session | **Unit 5** (CLI & Bundles) | FR-03, FR-04, FR-06 | `SECURITY-03`, `SECURITY-08` |
| **US-02**: File System & Shell Tools | **Unit 3** (Tool Registry & Built-ins) | FR-05 | `SECURITY-01`, `SECURITY-05`, `RES-02` |
| **US-03**: Durable Session History & Recovery | **Unit 1** (Kernel & Session Store) | FR-02 | `RES-03`, `PBT-01` |
| **US-04**: Programmatic SDK Turn Orchestration | **Unit 4** (Agent Loop) + **Unit 5** (SDK) | FR-01, FR-03, FR-04 | `RES-01`, `PBT-02` |
| **US-05**: Custom Plugin & Tool Registration | **Unit 1** (Kernel) + **Unit 3** (Tools) | FR-01, FR-05 | `PBT-01`, `PBT-03` |
| **US-06**: Security & Resiliency Hardening | **All Units** (Cross-Cutting) | NFR-SEC, NFR-RES, NFR-PBT | `SECURITY-01`–`08`, `RES-01`–`03`, `PBT-01`–`03` |

---

## 2. Unit-Level Scope Breakdown

### Unit 1: Core Kernel & Event Sourcing Store
- **Stories**: `US-03`, `US-05` (part)
- **Requirements**: `FR-01.1`, `FR-01.2`, `FR-01.3`, `FR-02.1`, `FR-02.2`, `FR-02.3`
- **Extensions**: `RES-03` (atomic JSONL writes), `PBT-01` (Hypothesis round-trip serialization tests)

### Unit 2: LLM Adapter & Streaming Engine
- **Stories**: `US-01` (part), `US-04` (part)
- **Requirements**: `FR-04.1`, `FR-04.2`, `FR-04.3`
- **Extensions**: `RES-01` (exponential backoff retry with jitter), `SECURITY-07` (zero hardcoded API keys)

### Unit 3: Scoped Tool Registry & Built-in Tools
- **Stories**: `US-02`, `US-05`
- **Requirements**: `FR-05.1`, `FR-05.2`, `FR-05.3`
- **Extensions**: `SECURITY-05` (Pydantic schema validation & path traversal blocks), `RES-02` (subprocess kill tree on timeout)

### Unit 4: Agent Loop & Turn Orchestrator
- **Stories**: `US-01` (part), `US-04`
- **Requirements**: `FR-03.1`, `FR-03.2`, `FR-03.3`
- **Extensions**: `PBT-02` (monotonic sequence invariants), `SECURITY-08` (error sanitization)

### Unit 5: Bundles, CLI Launcher & SDK Interface
- **Stories**: `US-01`, `US-04`
- **Requirements**: `FR-06.1`, `FR-06.2`
- **Extensions**: `SECURITY-03` (structured logging with credential masking)
