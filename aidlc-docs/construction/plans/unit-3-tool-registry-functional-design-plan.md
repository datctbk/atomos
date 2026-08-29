# Unit 3 Functional Design Plan: Scoped Tool Registry & Built-in Tools

## Purpose
Plan the detailed business logic, Pydantic BaseTool schema generator, scoped registry lookup, interceptor hooks, and built-in FS/Shell tools for **Unit 3: Scoped Tool Registry & Built-ins** (`python/atomos/tools/`).

---

## Execution Checklist

- [x] **Step 1: Collect User Functional Preferences for Unit 3** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 3 Domain Entities Document** (`aidlc-docs/construction/unit-3-tool-registry/functional-design/domain-entities.md`)
- [x] **Step 4: Generate Unit 3 Business Logic Model** (`aidlc-docs/construction/unit-3-tool-registry/functional-design/business-logic-model.md`)
- [x] **Step 5: Generate Unit 3 Business Rules & Validation** (`aidlc-docs/construction/unit-3-tool-registry/functional-design/business-rules.md`)
- [ ] **Step 6: User Approval of Unit 3 Functional Design**

---

## Mandatory Artifacts to Generate
- `domain-entities.md`: Data models for `BaseTool[TParams]`, `ToolDefinition`, `ToolResult`, `ToolRegistry`, `ViewFileTool`, `WriteFileTool`, `ReplaceFileContentTool`, and `RunCommandTool`.
- `business-logic-model.md`: Tool execution pipeline (Schema Generation -> Validation -> Pre-Hook Interceptor -> Execution -> Post-Hook Formatting).
- `business-rules.md`: Path confinement rules, Pydantic parameter schema validation rules, and error return formats.

---

## Functional Design Questions for Unit 3

Please answer the following questions to guide the design of the tool registry and built-in tools.

### Question 1: Tool Execution Result Format
How should successful and failing tool execution results be returned to the LLM turn loop?

A) **Structured `ToolResult` Object with `success: bool`, `output: str`, and `error: str | None`** (Recommended: Provides clean sanitization and prevents unhandled internal exceptions from leaking into LLM context (`SECURITY-08`))

B) **Raw String / Dictionary Return**: Direct string or dictionary returned directly from the execute function

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Filesystem Tool Workspace Sandbox Confinement
How should filesystem tools (`view_file`, `write_to_file`, `replace_file_content`) enforce path confinement (`SECURITY-05`)?

A) **Workspace Root Confinement with Configurable Base Directory**: All paths are resolved relative to workspace root; paths attempting path traversal (`../`) outside the configured boundary raise `SecurityAccessError` (recommended)

B) **Unrestricted Global Filesystem Access**: Tools can access any system path accessible to the operating system user

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Shell Command Execution Timeout & Process Tree Termination (RES-02)
How should `run_command` handle subprocess timeouts and runaway background processes?

A) **Process Group Termination (`os.killpg`) with Default 60s Timeout**: Launches subprocess in a new process group (`preexec_fn=os.setsid`) and terminates the entire process tree on timeout to prevent zombie processes (`RES-02`) (recommended)

B) **Standard `subprocess.run(timeout=60)` Single-PID Kill**: Terminates only the root parent process

X) Other (please describe after [Answer]: tag below)

[Answer]: A
