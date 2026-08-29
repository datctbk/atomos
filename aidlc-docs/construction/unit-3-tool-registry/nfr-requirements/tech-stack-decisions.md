# Unit 3 Tech Stack Decisions: Scoped Tool Registry & Built-ins

This document records the technology and library selections for Unit 3.

---

## 1. Technology Choices & Libraries

| Capability | Selected Library | Version | Rationale |
|---|---|---|---|
| **Path Manipulation & Security** | `pathlib.Path` | Python stdlib | Built-in cross-platform path resolution and `is_relative_to()` confinement validation. |
| **Async Subprocess Runner** | `asyncio.subprocess` + `os.killpg` | Python stdlib | Non-blocking command execution with POSIX process group tree killing (`RES-02`). |
| **Schema Validation** | `pydantic` | `>=2.6.0` | Rust-backed parameter validation and automated JSON schema generation. |
| **Testing & Property Fuzzing** | `hypothesis` + `pytest` | `>=6.100.0` | Comprehensive path traversal fuzzing and string replacement property tests. |

---

## 2. Directory & Packaging Specifications
- **Package Path**: `python/atomos/tools/`
  - `python/atomos/tools/base.py`: `BaseTool[TParams]`, `ToolResult`, `ToolRegistry`.
  - `python/atomos/tools/builtins/fs.py`: `ViewFileTool`, `WriteFileTool`, `ReplaceFileTool`.
  - `python/atomos/tools/builtins/shell.py`: `RunCommandTool`.
