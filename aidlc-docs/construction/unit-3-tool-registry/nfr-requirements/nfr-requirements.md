# Unit 3 NFR Requirements: Scoped Tool Registry & Built-ins

This document specifies the non-functional requirements, path confinement policies (`SECURITY-05`), subprocess process group termination rules (`RES-02`), and output truncation limits for Unit 3.

---

## 1. Security & Sandboxing Constraints

### NFR-SEC-01: Strict Workspace Path Confinement (SECURITY-05)
- **Rule**: All filesystem operations (`view_file`, `write_to_file`, `replace_file_content`) must resolve paths against a configured `workspace_root`.
- **Enforcement**: Canonical paths (`pathlib.Path.resolve()`) must satisfy `resolved_path.is_relative_to(workspace_root.resolve())`.
- **Violation Action**: Block execution and return sanitized `ToolResult(success=False, error="SecurityAccessError: Path traversal outside workspace root is blocked")`.

### NFR-SEC-02: Output Error Sanitization (SECURITY-08)
- **Rule**: Uncaught internal tool exceptions must never leak raw system stack traces into LLM context.
- **Rule**: All exceptions are captured into `ToolResult.error` with descriptive, sanitized messages.

---

## 2. Resiliency & Process Management (RES-02)

### NFR-RES-01: Subprocess Process Tree Termination
- **Rule**: `run_command` commands must spawn in a dedicated POSIX process group using `preexec_fn=os.setsid`.
- **Rule**: On timeout (default 60s), `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)` is invoked to cleanly terminate child and grandchild processes, preventing zombie/orphaned processes.

---

## 3. Performance & Output Truncation

### NFR-PERF-01: Context-Safe Output Truncation
- **Rule**: Tool output text is capped at 50KB or 800 lines (whichever is reached first).
- **Format**: When truncated, output ends with `\n... [Output truncated: capped at 800 lines / 50KB]`.

---

## 4. Property-Based Testing Requirements (PBT-01)

### NFR-PBT-01: Path Confinement Traversal Fuzzing
- **Property**: For all generated path strings with `../`, absolute roots, or symlink chains outside `workspace_root`, `resolve_safe_path` consistently raises `SecurityAccessError`.
