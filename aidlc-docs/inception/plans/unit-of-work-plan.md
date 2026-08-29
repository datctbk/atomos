# Units of Work Decomposition Plan

## Purpose
Plan the breakdown of the DeepSeek Harness Python codebase into modular, testable units of work for the Construction Phase, and map all User Stories and Requirements to their respective units.

---

## Execution Checklist

- [x] **Step 1: Collect User Decomposition Preferences** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit of Work Definitions** (`aidlc-docs/inception/application-design/unit-of-work.md`)
- [x] **Step 4: Generate Unit Dependency Matrix** (`aidlc-docs/inception/application-design/unit-of-work-dependency.md`)
- [x] **Step 5: Generate Unit-to-Story Map** (`aidlc-docs/inception/application-design/unit-of-work-story-map.md`)
- [ ] **Step 6: User Approval of Unit Decomposition**

---

## Mandatory Artifacts to Generate
- `unit-of-work.md`: Definitions, directory structures, and responsibilities for each development unit.
- `unit-of-work-dependency.md`: Inter-unit dependencies, construction sequence, and contract boundaries.
- `unit-of-work-story-map.md`: Traceability mapping each User Story (`US-01` to `US-06`) to its primary unit.

---

## Decomposition Planning Questions

Please answer the following questions to finalize the unit boundaries and construction sequence.

### Question 1: Unit Granularity Strategy
How granular should the implementation units be structured for the Construction Phase?

A) **5 Modular Subsystem Units** (Recommended):
  - Unit 1: Core Kernel & Event Sourcing (`dsh.core.context`, `dsh.core.events`, `dsh.core.session`)
  - Unit 2: LLM Adapter & Streaming Engine (`dsh.llm`, `dsh.llm.providers`)
  - Unit 3: Scoped Tool Registry & Built-ins (`dsh.tools`, `dsh.tools.fs`, `dsh.tools.shell`)
  - Unit 4: Agent Loop & Turn Orchestrator (`dsh.core.agent_loop`, `dsh.core.system_prompt`)
  - Unit 5: Bundles, CLI Launcher & SDK (`dsh.cli`, `dsh.sdk`, `dsh.profiles`)

B) **3 Consolidated Units**:
  - Unit 1: Core Kernel & Engine (`dsh.core`, `dsh.session`, `dsh.events`)
  - Unit 2: LLM & Tooling Pipeline (`dsh.llm`, `dsh.tools`)
  - Unit 3: Agent Orchestration, CLI & SDK (`dsh.agent_loop`, `dsh.cli`, `dsh.sdk`)

C) **Single Monolithic Unit**: Implement all modules simultaneously in a single Construction pass

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Python Code Directory Structure
Where should the new Python codebase be located in the workspace?

A) **`python/dsh/`** (Recommended): Standard Python package structure within the repository root with `pyproject.toml` at `python/` or project root

B) **`dsh_py/`**: Top-level directory for the Python implementation

C) **`packages/python/`**: Nested monorepo package pattern

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Construction Iteration Sequence
In what order should the units be built and verified during the Construction Phase?

A) **Bottom-Up Layered**: Core Kernel/Session -> LLM Client -> Tool Pipeline -> Agent Loop -> CLI/SDK (recommended for solid foundational testing with PBT)

B) **Outside-In User Journey**: CLI/SDK Shell -> Agent Loop -> Tool Pipeline -> LLM & Kernel

X) Other (please describe after [Answer]: tag below)

[Answer]: A
