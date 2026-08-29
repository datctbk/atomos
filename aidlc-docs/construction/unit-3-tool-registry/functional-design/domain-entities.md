# Unit 3 Domain Entities: Scoped Tool Registry & Built-ins

This document defines the domain models, parameter schema structures, tool interfaces, and built-in filesystem and shell tool models for Unit 3 in `atomos`.

---

## 1. Domain Entity Class Diagram

```mermaid
classDiagram
    class BaseTool~TParams~ {
        <<abstract>>
        +str name
        +str description
        +type[TParams] params_model
        +to_openai_tool() dict
        +execute(params) ToolResult
    }

    class ToolResult {
        +bool success
        +str output
        +str error
        +to_dict() dict
    }

    class ToolRegistry {
        +dict tools
        +register_tool(tool) Disposable
        +get_tool(name) BaseTool
        +list_tools() list
        +execute_tool(name, raw_json_args) ToolResult
    }

    class ViewFileInput {
        +str file_path
        +int offset
        +int limit
    }

    class WriteFileInput {
        +str file_path
        +str content
        +bool overwrite
    }

    class ReplaceFileInput {
        +str file_path
        +str old_string
        +str new_string
        +bool replace_all
    }

    class RunCommandInput {
        +str command
        +str cwd
        +int timeout_seconds
    }

    class ViewFileTool
    class WriteFileTool
    class ReplaceFileTool
    class RunCommandTool

    BaseTool <|-- ViewFileTool
    BaseTool <|-- WriteFileTool
    BaseTool <|-- ReplaceFileTool
    BaseTool <|-- RunCommandTool
    ViewFileTool ..> ViewFileInput
    WriteFileTool ..> WriteFileInput
    ReplaceFileTool ..> ReplaceFileInput
    RunCommandTool ..> RunCommandInput
    ToolRegistry *-- BaseTool
    BaseTool ..> ToolResult : returns
```

---

## 2. Entity Specifications

### 2.1 `BaseTool[TParams]`
- **Fields**:
  - `name`: `str` — Unique tool identifier matching model invocation strings (e.g. `view_file`).
  - `description`: `str` — Detailed explanation of purpose and usage for prompt injection.
  - `params_model`: `type[TParams]` — Pydantic `BaseModel` defining schema and field constraints.
- **Methods**:
  - `to_openai_tool()`: Auto-generates OpenAI function schema (`{"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}`).
  - `async def execute(params: TParams) -> ToolResult`: Strongly-typed execution handler.

### 2.2 `ToolResult`
- **Fields**:
  - `success`: `bool` — Indicates if tool execution completed without internal or permission errors.
  - `output`: `str` — String output formatted for LLM context injection.
  - `error`: `str | None` — Sanitized error message (`SECURITY-08`).

### 2.3 `ToolRegistry`
- **Responsibilities**:
  - Registers tools and produces `Disposable` unbinding tokens.
  - Generates combined tool definitions array for `BaseLLMAdapter.stream()`.
  - Parses incoming JSON argument strings against tool `params_model` and executes tool with error containment.
