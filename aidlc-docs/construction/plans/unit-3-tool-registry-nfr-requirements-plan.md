# Unit 3 NFR Requirements Plan: Scoped Tool Registry & Built-in Tools

## Purpose
Assess and define non-functional requirements, security controls (`SECURITY-05`, `SECURITY-08`), output truncation limits, and subprocess isolation policies (`RES-02`) for **Unit 3: Scoped Tool Registry & Built-ins** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Preferences for Unit 3** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 3 NFR Requirements Document** (`aidlc-docs/construction/unit-3-tool-registry/nfr-requirements/nfr-requirements.md`)
- [x] **Step 4: Generate Unit 3 Tech Stack Decisions Document** (`aidlc-docs/construction/unit-3-tool-registry/nfr-requirements/tech-stack-decisions.md`)
- [ ] **Step 5: User Approval of Unit 3 NFR Requirements**

---

## Mandatory Artifacts to Generate
- `nfr-requirements.md`: Concrete path confinement policies (`SECURITY-05`), output size limits (max lines/bytes), execution timeouts (`RES-02`), and sanitized error reporting (`SECURITY-08`).
- `tech-stack-decisions.md`: Standard library tools (`pathlib`, `asyncio.subprocess`, `os.killpg`) and Pydantic schema validation.

---

## NFR Planning Questions for Unit 3

Please answer the following questions to establish the non-functional specifications for Unit 3.

### Question 1: Tool Output Size Limit & Truncation Strategy
What output truncation threshold should be enforced on large tool returns (e.g. huge `view_file` or verbose `run_command` logs) to avoid exhausting LLM context windows?

A) **Configurable Byte & Line Limits (Default 50KB / 800 lines with explicit truncation notice)** (Recommended: Appends `\n... [Output truncated: showing first 800 lines / 50KB]`)

B) **Unbounded Output Buffer**: Return complete unmodified command and file outputs

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Subprocess Execution Environment Isolation
How should the environment variables passed to `run_command` subprocesses be filtered?

A) **Sanitized Inherited Environment**: Inherits `PATH`, `HOME`, `USER`, but automatically blocks dangerous environment overrides (recommended)

B) **Completely Isolated Minimal Environment**: Only `PATH` and `HOME` provided

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Property-Based Testing Strategy for Path Confinement (PBT-01, SECURITY-05)
What invariants should be tested with Hypothesis for filesystem path validation?

A) **Arbitrary Relative & Dot-Dot (`../`) Traversal Generators**: Generating random directory tree traversals to verify that `resolve_safe_path` strictly prevents escaping `workspace_root` (recommended)

B) **Static Path Matrix Tests**: Fixed list of test paths

X) Other (please describe after [Answer]: tag below)

[Answer]: A
