# Unit 1 NFR Requirements Plan: Core Kernel & Event Sourcing Store

## Purpose
Assess and define the non-functional requirements, quality attributes, performance targets, and tech stack choices for **Unit 1: Core Kernel & Event Sourcing Store** for `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Preferences for Unit 1** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 1 NFR Requirements Document** (`aidlc-docs/construction/unit-1-core-kernel/nfr-requirements/nfr-requirements.md`)
- [x] **Step 4: Generate Unit 1 Tech Stack Decisions Document** (`aidlc-docs/construction/unit-1-core-kernel/nfr-requirements/tech-stack-decisions.md`)
- [ ] **Step 5: User Approval of Unit 1 NFR Requirements**

---

## Mandatory Artifacts to Generate
- `nfr-requirements.md`: Specific performance, resilience, security, and property-based testing constraints for Unit 1.
- `tech-stack-decisions.md`: Library choices (e.g. `pydantic`, `hypothesis`, `pytest-asyncio`, `anyio`/`asyncio`).

---

## NFR Planning Questions for Unit 1

Please answer the following questions to establish the non-functional specifications for Unit 1.

### Question 1: Session Storage Directory & File Permissions
Where should the default session JSONL files be stored, and what access controls should be applied (`SECURITY-01`)?

A) **`~/.atomos/sessions/` with restricted user-only permissions (`0o700` directory, `0o600` files)** (Recommended for local security)

B) **`.atomos/sessions/` within active workspace root**

C) **Configurable via `ATOMOS_HOME` or `ATOMOS_SESSION_DIR` environment variable** (defaults to `~/.atomos/sessions/`)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: In-Memory Event Ingestion Performance Target
What latency target should `append_event()` achieve for in-memory appending and atomic disk write?

A) **Sub-millisecond (< 2ms per event)**: Using fast buffered append with OS-level fsync/flush (recommended for interactive streaming)

B) **Standard (< 10ms per event)**: Standard synchronous file append

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Property-Based Testing Strategy for Event Serializer (PBT-01)
Which property-based testing framework and test generator strategies should be configured for Unit 1?

A) **`hypothesis` with custom composite strategies for `SessionEvent` and nested payloads** (Recommended for exhaustive edge case shrinking)

B) **Basic random fuzzing with `pytest` parameterization**

X) Other (please describe after [Answer]: tag below)

[Answer]: A
