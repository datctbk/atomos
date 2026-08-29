# Requirements Document: DeepSeek Harness Python Reimplementation

## Intent Analysis Summary

- **User Request**: Reimplement DeepSeek Harness in Python
- **Request Type**: Reimplementation / Language Port / Architecture Migration
- **Scope Estimate**: System-wide (Core micro-kernel, Agent Loop, Session Event Store, Tool Pipeline, LLM Streaming Adapters, Profiles/Bundles, and CLI/SDK)
- **Complexity Estimate**: Complex

---

## 1. Functional Requirements

### FR-01: Micro-Kernel & Plugin Framework (Cordis for Python)
- **FR-01.1**: Context container managing service registrations, lifecycle hooks, and dependency injection.
- **FR-01.2**: Typed event emission with support for:
  - **Durable session events**: Emitted and appended to the session log.
  - **Agent live events**: Multi-stage lifecycle (`agent/pre-step`, `agent/request`, `agent/turn-stopping`).
  - **Waterfall pipelines**: Middleware handlers invoking `await next()` to rewrite or validate payloads.
- **FR-01.3**: Disposable / reversible effects for clean plugin unloading.

### FR-02: Durable Session & Event Sourcing Store
- **FR-02.1**: Append-only event log recording all turn facts (`turn/start`, `user/message`, `assistant/chunk`, `assistant/message`, `tool/call`, `tool/result`, `turn/end`).
- **FR-02.2**: Serialization & deserialization to JSON/JSONL format.
- **FR-02.3**: Session recovery, compaction, and history replay.

### FR-03: Agent Turn & Step Execution Loop
- **FR-03.1**: Inbox management with immediate wakeup messages and queued context injection.
- **FR-03.2**: Turn lifecycle: Claim input -> compile system prompt & tool schemas -> execute step -> stream model -> invoke tools -> continue until turn criteria fulfilled.
- **FR-03.3**: Multi-step iterations with continuation conditions and loop termination safeguards.

### FR-04: LLM Streaming & Provider Adapters
- **FR-04.1**: Unified asynchronous LLM client interface for DeepSeek and OpenAI-compatible providers.
- **FR-04.2**: Streaming chunk handling, incremental tool call accumulation, and token usage accounting.
- **FR-04.3**: Fallback and retry handling with backoff for transient provider errors.

### FR-05: Scoped Tool Registry & Execution Pipeline
- **FR-05.1**: Schema-driven tool definitions using Pydantic models with parameter validation.
- **FR-05.2**: Interceptor pipeline: Pre-execution validation -> User approval gate -> Execution -> Post-execution format.
- **FR-05.3**: Built-in standard tool suite:
  - Filesystem (`view_file`, `write_to_file`, `replace_file_content`, `list_dir`)
  - Subprocess shell execution (`run_command` with timeout and streaming output)
  - MCP (Model Context Protocol) client integration.

### FR-06: Profiles, Bundles, and CLI Launcher
- **FR-06.1**: Composable configuration layers (Base bundle, Headless runner, CLI app, SDK server).
- **FR-06.2**: Command-line interface (`dsh` / `python -m dsh`) supporting `--profile`, interactive chat, and batch task execution.

---

## 2. Non-Functional Requirements & Extension Constraints

### NFR-SEC: Security Baseline (Enforced as Blocking Constraints)
- **SECURITY-01 (Data Storage Security)**: Secure file permissions on session logs and workspace data caches.
- **SECURITY-03 (Structured Logging)**: Python `logging` / `structlog` with correlation IDs, log levels, and automatic masking of API keys (`DEEPSEEK_API_KEY`, `OPENAI_API_KEY`) and sensitive credentials.
- **SECURITY-05 (Input Validation)**: Pydantic schemas validating all tool arguments and API payloads before execution.
- **SECURITY-07 (Secret Management)**: API keys and sensitive configuration loaded strictly from environment variables or `.env` files; zero hardcoded secrets.
- **SECURITY-08 (Error Sanitization)**: Raw internal stack traces sanitized in LLM conversation contexts while preserving full diagnostic logs locally.

### NFR-RES: Resiliency Baseline (Design-Time Best Practices)
- **RES-01 (Fault Tolerance & Retries)**: Exponential backoff with jitter for LLM stream disconnections and network timeouts.
- **RES-02 (Process Isolation & Timeouts)**: Strict execution timeouts and process kill-trees on subprocess shell commands to prevent zombie processes.
- **RES-03 (Atomic State Persistence)**: Atomic file writes (write to temp file then rename) for session logs to prevent corruption during unexpected shutdowns.

### NFR-PBT: Property-Based Testing (Enforced via Hypothesis)
- **PBT-01 (Round-Trip Properties)**: Round-trip serialization/deserialization for `SessionEvent` schemas, tool parameter schemas, and message dictionaries (`deserialize(serialize(x)) == x`).
- **PBT-02 (State Transition Invariants)**: Session event log monotonically increases and maintains strictly ordered event IDs across turns.
- **PBT-03 (Idempotence & Sanitization)**: String sanitizers and prompt compilers produce identical outputs upon repeated applications (`clean(clean(s)) == clean(s)`).

---

## 3. Technology Choices (Python Stack)
- **Language**: Python `>=3.11` (utilizing modern `asyncio`, type hints, `match`/`case`, and generic protocols).
- **Package Manager**: `uv` or `pip` / `pyproject.toml` (standard packaging).
- **Schema & Validation**: `pydantic` `>=2.0`.
- **HTTP / Async Client**: `httpx` / `aiohttp` for streaming LLM calls.
- **CLI Framework**: `typer` or `click` / `argparse`.
- **Testing**: `pytest`, `pytest-asyncio`, and `hypothesis` for Property-Based Testing.
- **Code Quality**: `ruff` (formatting and linting), `mypy` (strict static type checking).
