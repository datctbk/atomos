# Unit 3 Business Rules & Validation: Scoped Tool Registry & Built-ins

This document defines the invariants, path confinement rules (`SECURITY-05`), subprocess process group termination policies (`RES-02`), and property testing invariants.

---

## 1. Core Invariants & Business Rules

### BR-TOOL-01: Auto OpenAI Schema Generation
- **Rule**: Every `BaseTool` subclass MUST auto-generate its JSON schema parameters directly from `params_model.model_json_schema()`.
- **Validation**: Schema output contains valid JSON Schema type definitions with field descriptions and required array.

### BR-TOOL-02: Strict Path Confinement (`SECURITY-05`)
- **Rule**: All filesystem operations (`view_file`, `write_to_file`, `replace_file_content`) MUST reject paths attempting path traversal (`../`) outside the configured `workspace_root`.
- **Validation**: `resolved_path.is_relative_to(workspace_root.resolve()) == True`. Violations return `ToolResult(success=False, error="SecurityAccessError: Access outside workspace root is blocked")`.

### BR-TOOL-03: Process Tree Termination on Timeout (`RES-02`)
- **Rule**: Commands executed via `run_command` MUST execute in an isolated process group and terminate the complete process tree on timeout.
- **Verification**: Zero orphaned child processes or zombie shell processes remain after timeout triggers.

### BR-TOOL-04: Error Containment (`SECURITY-08`)
- **Rule**: Tool execution failures MUST NOT throw unhandled exceptions to the agent loop. All exceptions are caught and sanitized into `ToolResult(success=False, error=...)`.

---

## 2. Testable Properties for Property-Based Testing (PBT-01)

| Property Name | Category | Description |
|---|---|---|
| `prop_path_confinement_sandbox` | **Security Invariant** | For any arbitrary path traversal string containing `../` escaping workspace root, `resolve_safe_path` always raises `SecurityAccessError`. |
| `prop_replace_file_content_idempotence` | **Data Transformation** | Replacing `A` with `B` in text containing exact match `A` succeeds and contains `B`. |
