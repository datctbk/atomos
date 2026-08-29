# Unit 3 Code Generation Plan: Scoped Tool Registry & Built-ins

## 1. Unit Context & Traceability

- **Unit Name**: `unit-3-tool-registry`
- **Target Package Path**: `python/atomos/tools/`
- **Target Test Path**: `python/tests/`
- **Mapped User Stories**: `US-02` (Tool Execution & Subprocess Orchestration), `US-03` (Context Lifecycle & Scoped Bundle Provisioning), `US-06` (Security & Resiliency Hardening)
- **Mapped Requirements**: `FR-02.1`–`FR-02.5`, `NFR-SEC-01`, `NFR-SEC-02`, `NFR-RES-01`, `NFR-PERF-01`, `SECURITY-05`, `SECURITY-08`, `RES-02`, `PBT-01`

---

## 2. Step-by-Step Implementation Sequence

### Step 1: Base Tool Models, Registry & Truncator (`base.py`)
- [x] Create `python/atomos/tools/base.py` implementing:
  - `ToolResult` (structured execution output with sanitized error).
  - `BaseTool[TParams]` generic abstract base generating OpenAI schemas (`to_openai_tool()`).
  - `ToolRegistry` with scoped registrations producing `Disposable` tokens, schema lookups, and error containment (`SECURITY-08`).
  - `truncate_output` capping outputs at 50KB or 800 lines.
- [x] Create `python/atomos/tools/__init__.py` exposing tools namespace.

### Step 2: Filesystem Built-in Tools & Path Sandbox (`builtins/fs.py`)
- [x] Create `python/atomos/tools/builtins/__init__.py`.
- [x] Create `python/atomos/tools/builtins/fs.py` implementing:
  - `PathSandbox` and `SecurityAccessError` enforcing workspace boundary confinement (`SECURITY-05`).
  - `ViewFileTool` (`view_file`) with line numbering, offset, and limit.
  - `WriteFileTool` (`write_to_file`) with parent directory creation and overwrite safety.
  - `ReplaceFileTool` (`replace_file_content`) with exact match replacements.

### Step 3: Shell Built-in Tool & Subprocess Process Group Runner (`builtins/shell.py`)
- [x] Create `python/atomos/tools/builtins/shell.py` implementing:
  - `ProcessGroupRunner` spawning subprocesses with `preexec_fn=os.setsid` and executing graceful `SIGTERM` followed by forceful `SIGKILL` on timeout (`RES-02`).
  - `RunCommandTool` (`run_command`) executing commands within sandboxed directory.

### Step 4: Implement Unit & Property-Based Test Suites
- [x] Create `python/tests/unit/test_tools_base.py` testing schema generation, registry dispatch, and error containment.
- [x] Create `python/tests/unit/test_tools_fs.py` testing `view_file`, `write_to_file`, `replace_file_content`, and directory traversal blocks.
- [x] Create `python/tests/unit/test_tools_shell.py` testing `run_command` and timeout kill mechanics.
- [x] Create `python/tests/property/test_tools_pbt.py` using `hypothesis` testing:
  - `prop_path_confinement_sandbox`: Random directory traversal escaping attempts strictly raise `SecurityAccessError` (`PBT-01`, `SECURITY-05`).
  - `prop_replace_file_content_idempotence`: String replacement correctness.

### Step 5: Run Verification Tests & Generate Documentation Summary
- [x] Run `pytest`, `hypothesis`, `ruff`, and `mypy` test suite to verify 100% pass rate.
- [x] Create `aidlc-docs/construction/unit-3-tool-registry/code/code-summary.md` documenting implementation details, test results, and compliance.
