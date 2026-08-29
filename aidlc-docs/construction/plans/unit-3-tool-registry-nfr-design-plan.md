# Unit 3 NFR Design Plan: Scoped Tool Registry & Built-in Tools

## Purpose
Design the architectural patterns, sandbox confinement components (`SECURITY-05`), subprocess process group termination runners (`RES-02`), and output truncators for **Unit 3: Scoped Tool Registry & Built-ins** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Design Preferences for Unit 3** (Completed with user answers: A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 3 NFR Design Patterns Document** (`aidlc-docs/construction/unit-3-tool-registry/nfr-design/nfr-design-patterns.md`)
- [x] **Step 4: Generate Unit 3 Logical Components Document** (`aidlc-docs/construction/unit-3-tool-registry/nfr-design/logical-components.md`)
- [ ] **Step 5: User Approval of Unit 3 NFR Design**

---

## Mandatory Artifacts to Generate
- `nfr-design-patterns.md`: Path sandbox resolver pattern (`SECURITY-05`), process group subprocess runner (`RES-02`), and output truncation filter.
- `logical-components.md`: Logical component specifications for `PathSandbox`, `ProcessGroupRunner`, `OutputTruncator`, and `ToolRegistryInterceptor`.

---

## NFR Design Questions for Unit 3

Please answer the following questions to guide the non-functional design of the tool execution layer.

### Question 1: Path Sandbox Enforcement Architecture
How should path resolution and sandboxing be integrated into filesystem tools (`SECURITY-05`)?

A) **Shared `PathSandbox` Utility Component**: A dedicated helper class injected via Context or default instance resolving canonical paths and asserting `path.is_relative_to(workspace_root)` (recommended for consistency)

B) **Inline Verification in Each Tool**: Every filesystem tool implements its own path resolution logic directly

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Process Group Termination Implementation Details (RES-02)
How should `ProcessGroupRunner` manage process tree signals on POSIX systems?

A) **Graceful `SIGTERM` followed by forceful `SIGKILL` on timeout**: On timeout, sends `signal.SIGTERM` to process group, waits 1.0s, then sends `signal.SIGKILL` if processes remain (recommended)

B) **Immediate `SIGKILL` on timeout**: Instantly sends `signal.SIGKILL` to the process group

X) Other (please describe after [Answer]: tag below)

[Answer]: A
