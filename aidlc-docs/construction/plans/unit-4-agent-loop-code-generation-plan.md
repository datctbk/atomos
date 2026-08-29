# Unit 4 Code Generation Plan: Agent Loop & Turn Driver

## 1. Unit Context & Traceability

- **Unit Name**: `unit-4-agent-loop`
- **Target Package Path**: `python/atomos/agent/` and `python/atomos/core/`
- **Target Test Path**: `python/tests/`
- **Mapped User Stories**: `US-01` (Interactive CLI Agent Session), `US-04` (Programmatic SDK Turn Orchestration), `US-06` (Security & Resiliency Hardening)
- **Mapped Requirements**: `FR-01.1`–`FR-01.6`, `NFR-PERF-01`, `NFR-PERF-02`, `NFR-REL-01`, `NFR-REL-02`, `PBT-01`

---

## 2. Step-by-Step Implementation Sequence

### Step 1: Implement Dynamic System Prompt Synthesizer (`system_prompt.py`)
- [x] Create `python/atomos/core/system_prompt.py` implementing:
  - `build_system_prompt(workspace_path, custom_instructions, tools_summary)` providing environment context, OS metadata, and safety guidance.

### Step 2: Implement Agent Loop, Context Compactor & Turn Driver (`loop.py`)
- [x] Create `python/atomos/agent/loop.py` (and re-export in `python/atomos/core/agent_loop.py`) implementing:
  - `AgentStatus` enum and `TurnOptions` Pydantic model.
  - `ContextCompactor` with sliding window message history compaction.
  - `AgentLoop` coordinating LLM streaming, token yielding, multi-tool execution, session persistence, and non-blocking event broadcasting.
- [x] Create `python/atomos/agent/__init__.py` exposing agent types.

### Step 3: Implement Unit & Property-Based Test Suites
- [x] Create `python/tests/unit/test_context_compactor.py` testing sliding window compaction preserving system prompts.
- [x] Create `python/tests/unit/test_agent_loop.py` testing single-turn text streaming, multi-turn tool execution, cancellation, and max iterations guardrails.
- [x] Create `python/tests/property/test_agent_pbt.py` using `hypothesis` testing:
  - `prop_context_compaction_invariants`: Preserving system message and context budget (`PBT-01`).
  - `prop_agent_loop_monotonic_events`: Strictly monotonic gapless sequence IDs during multi-iteration turns (`PBT-01`).

### Step 4: Run Verification Tests & Generate Documentation Summary
- [x] Run `pytest`, `hypothesis`, `ruff`, and `mypy` test suite to verify 100% pass rate.
- [x] Create `aidlc-docs/construction/unit-4-agent-loop/code/code-summary.md` documenting implementation details, test results, and compliance.
