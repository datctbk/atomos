# Units of Work: DeepSeek Harness Python

This document defines the 5 modular implementation units, directory structure, package paths, and responsibilities for the Construction Phase.

---

## 1. Directory Structure

```text
python/
├── pyproject.toml                     # Package manifest, dependencies, tool configs
├── README.md                          # Python package documentation
├── atomos/                            # Primary Python package (cli binary: atomos)
│   ├── __init__.py
│   ├── core/                          # [Unit 1 & Unit 4]
│   │   ├── __init__.py
│   │   ├── context.py                 # Dependency injection & plugin lifecycle
│   │   ├── events.py                  # EventBus & waterfall interceptors
│   │   ├── session.py                 # Append-only session event store
│   │   ├── agent_loop.py              # Turn coordinator & multi-step execution
│   │   └── system_prompt.py           # Dynamic system prompt synthesis
│   ├── llm/                           # [Unit 2]
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract LLM adapter & message models
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── deepseek.py            # DeepSeek SSE streaming client
│   │       └── openai.py              # OpenAI-compatible streaming client
│   ├── tools/                         # [Unit 3]
│   │   ├── __init__.py
│   │   ├── base.py                    # Pydantic BaseTool schema generator
│   │   ├── registry.py                # Scoped tool registry & interceptor pipeline
│   │   └── builtins/
│   │       ├── __init__.py
│   │       ├── fs.py                  # File viewing, writing, editing tools
│   │       └── shell.py               # Subprocess command execution with timeouts
│   ├── boot/                          # [Unit 5]
│   │   ├── __init__.py
│   │   ├── profile.py                 # Profile layering & bundle mounting
│   │   └── bundles/
│   │       ├── __init__.py
│   │       └── base.py                # Base bundle composition
│   ├── cli/                           # [Unit 5]
│   │   ├── __init__.py
│   │   └── main.py                    # Terminal CLI entrypoint (atomos / python -m atomos)
│   └── sdk/                           # [Unit 5]
│       ├── __init__.py
│       └── client.py                  # Programmatic async Python client
└── tests/                             # Test suites across all units
    ├── unit/
    ├── property/                      # Hypothesis Property-Based Testing
    └── integration/
```

---

## 2. Unit Definitions

### Unit 1: Core Kernel & Event Sourcing Store
- **Directory**: `python/dsh/core/` (`context.py`, `events.py`, `session.py`)
- **Responsibilities**:
  - `Context` class providing typed service registration and reversible `Disposable` tokens.
  - `EventBus` supporting asynchronous event broadcasting and waterfall middleware pipelines (`await next()`).
  - `SessionStore` and `SessionEvent` models implementing append-only event logging with atomic JSONL file persistence.
- **Key Constraints**:
  - `PBT-01`: Lossless round-trip serialization/deserialization for `SessionEvent` via Hypothesis.
  - `RES-03`: Atomic file writes (temp file + rename).

### Unit 2: LLM Adapter & Streaming Engine
- **Directory**: `python/dsh/llm/` (`base.py`, `providers/deepseek.py`, `providers/openai.py`)
- **Responsibilities**:
  - Typed message data models (`LLMMessage`, `LLMChunk`).
  - Asynchronous streaming generator parsing SSE token chunks and tool call fragments.
  - Provider adapters for DeepSeek and OpenAI-compatible endpoints.
- **Key Constraints**:
  - `RES-01`: Exponential backoff with jitter on streaming disconnections.
  - `SECURITY-07`: Credentials loaded from environment variables with zero hardcoded secrets.

### Unit 3: Scoped Tool Registry & Built-in Tools
- **Directory**: `python/dsh/tools/` (`base.py`, `registry.py`, `builtins/fs.py`, `builtins/shell.py`)
- **Responsibilities**:
  - `BaseTool[TParams]` generating OpenAI JSON Schema from Pydantic `BaseModel`.
  - `ToolRegistry` executing validation, pre-execution hooks, execution, and post-execution formatting.
  - Built-in filesystem tools (`view_file`, `write_to_file`, `replace_file_content`).
  - Built-in shell tool (`run_command`) with process group timeout termination.
- **Key Constraints**:
  - `SECURITY-05`: Strict parameter validation and path confinement checks.
  - `RES-02`: Subprocess tree timeout termination preventing zombie processes.

### Unit 4: Agent Loop & Dynamic Turn Orchestrator
- **Directory**: `python/dsh/core/` (`agent_loop.py`, `system_prompt.py`)
- **Responsibilities**:
  - Multi-step turn execution engine claiming user messages from inbox.
  - Dynamic prompt compilation combining registered sections and tool schemas.
  - Loop continuation logic handling intermediate tool call results and turn closure.
- **Key Constraints**:
  - `PBT-02`: Invariant verification for strictly monotonic session event sequences.
  - `SECURITY-08`: Error sanitization preventing internal stack trace leaks to LLM context.

### Unit 5: Bundles, CLI Launcher & SDK Interface
- **Directory**: `python/dsh/boot/`, `python/dsh/cli/`, `python/dsh/sdk/`
- **Responsibilities**:
  - Boot profile layering mechanism (`ProfileBoot`) mounting bundles onto Context.
  - Rich interactive terminal CLI (`dsh` / `python -m dsh`) with streaming markdown output.
  - Importable async Python SDK (`from dsh import Context, AgentLoop`).
- **Key Constraints**:
  - `SECURITY-03`: Structured logging with automated API key masking.
