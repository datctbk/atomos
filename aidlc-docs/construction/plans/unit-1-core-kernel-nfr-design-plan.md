# Unit 1 NFR Design Plan: Core Kernel & Event Sourcing Store

## Purpose
Design the architectural patterns, security controls, and logical components satisfying the non-functional requirements for **Unit 1: Core Kernel & Event Sourcing Store** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Design Preferences for Unit 1** (Completed with user answers: A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate NFR Design Patterns Document** (`aidlc-docs/construction/unit-1-core-kernel/nfr-design/nfr-design-patterns.md`)
- [x] **Step 4: Generate Logical Components Document** (`aidlc-docs/construction/unit-1-core-kernel/nfr-design/logical-components.md`)
- [ ] **Step 5: User Approval of Unit 1 NFR Design**

---

## Mandatory Artifacts to Generate
- `nfr-design-patterns.md`: Concrete implementation patterns for atomic file writing (`RES-03`), credential masking filters (`SECURITY-03`), and Hypothesis test strategies (`PBT-01`).
- `logical-components.md`: Logical component specifications for `AtomicFileWriter`, `RedactingLogFormatter`, and `HypothesisEventStrategy`.

---

## NFR Design Questions for Unit 1

Please answer the following questions to guide the non-functional component design.

### Question 1: Atomic File Persistence Implementation
How should the atomic file append and write mechanism be designed to prevent file corruption during sudden system shutdowns?

A) **Buffered Line-Append with Sync**: Open file descriptor with `os.O_WRONLY | os.O_CREAT | os.O_APPEND`, write JSON line, and invoke `os.fsync()` on critical events (recommended for maximum throughput and durability)

B) **Write-to-Temp-and-Rename for Full Session Snapshots**: Full state rewritten to `.tmp` file and atomically renamed (`os.replace`)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Credential Redaction Filter Architecture
How should automated token masking be integrated into the logging pipeline (`SECURITY-03`)?

A) **Custom `logging.Filter` with Regex Token Replacer**: A pluggable logging filter inspecting all log records and masking matching patterns (`sk-...`, `Bearer ...`, API key variables) before formatting (recommended)

B) **Wrapper Logger Protocol**: A dedicated wrapper class intercepting log messages before passing to standard logging

X) Other (please describe after [Answer]: tag below)

[Answer]: A
