# Unit 5 Code Generation Plan: Bundles, CLI & SDK

## 1. Unit Context & Traceability

- **Unit Name**: `unit-5-bundles-cli-sdk`
- **Target Package Path**: `python/atomos/boot/`, `python/atomos/cli/`, `python/atomos/sdk/`
- **Target Test Path**: `python/tests/`
- **Mapped User Stories**: `US-01` (Interactive CLI Agent Session), `US-02` (Local LLM Execution), `US-04` (Programmatic SDK Turn Orchestration), `US-06` (Security & Resiliency Hardening)
- **Mapped Requirements**: `FR-01`–`FR-05`, `NFR-PERF-01`, `NFR-RES-01`, `PBT-01`

---

## 2. Step-by-Step Implementation Sequence

### Step 1: Implement Bundles & Profile Bootstrapper (`atomos/boot/`)
- [x] Create `python/atomos/boot/bundles/base.py` and `__init__.py` implementing:
  - `BaseBundle` abstract lifecycle interface.
  - `CoreBundle`, `ToolsBundle`, `LLMBundle` mounting DI services.
- [x] Create `python/atomos/boot/profile.py` and `__init__.py` implementing:
  - `Profile` model with `bootstrap() -> tuple[Context, Session, AgentLoop]`.

### Step 2: Implement Programmatic SDK Client (`atomos/sdk/`)
- [x] Create `python/atomos/sdk/client.py` and `__init__.py` implementing:
  - `AtomosClient` async context manager.
  - `async def chat(prompt: str) -> AsyncIterator[str]` streaming generator.

### Step 3: Implement Typer CLI Application (`atomos/cli/`)
- [x] Create `python/atomos/cli/main.py` and `__init__.py` implementing:
  - Typer application with `run` and interactive REPL mode.
  - Flags: `--local / -l`, `--model / -m`, `--workspace / -w`, `--session / -s`, `--local-url`.
  - Rich Live rendering with Markdown streaming and tool event panels.
  - Ensure dual binary aliases in `pyproject.toml`: `atomos` and `atimos`.

### Step 4: Implement Unit & Property-Based Test Suites
- [x] Create `python/tests/unit/test_profile_bundles.py` testing DI wiring and local vs. cloud adapter selection.
- [x] Create `python/tests/unit/test_sdk_client.py` testing SDK lifecycle and streaming chat.
- [x] Create `python/tests/unit/test_cli_main.py` testing Typer CLI invocation and help output.
- [x] Create `python/tests/property/test_sdk_pbt.py` using `hypothesis` testing:
  - `prop_profile_config_precedence`: Verifying options precedence (`PBT-01`).
  - `prop_sdk_lifecycle_cleanup`: Verifying 100% context cleanup and file handle release (`PBT-01`).

### Step 5: Run Verification Tests & Generate Documentation Summary
- [x] Run full test suite (`pytest`, `hypothesis`, `ruff`, `mypy`).
- [x] Create `aidlc-docs/construction/unit-5-bundles-cli-sdk/code/code-summary.md` documenting implementation details and test results.
