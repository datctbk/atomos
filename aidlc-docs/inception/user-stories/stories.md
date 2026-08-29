# User Stories: DeepSeek Harness Python Reimplementation

## Story Overview & Mapping Matrix

| Story ID | Story Title | User Journey | Primary Persona | Mapped Requirements |
|---|---|---|---|---|
| **US-01** | Interactive CLI Agent Session | Journey 1: Interactive Terminal Developer | Alex (CLI Practitioner) | FR-03, FR-04, FR-06, NFR-SEC |
| **US-02** | File System & Shell Execution Tools | Journey 1: Interactive Terminal Developer | Alex (CLI Practitioner) | FR-05, NFR-SEC, NFR-RES |
| **US-03** | Durable Session History & Recovery | Journey 1 & 2: Developer Continuity | Alex / Taylor | FR-02, NFR-RES, NFR-PBT |
| **US-04** | Programmatic SDK Turn Orchestration | Journey 2: SDK & Embedded Integration | Taylor (Platform Engineer) | FR-01, FR-03, FR-04 |
| **US-05** | Custom Plugin & Tool Registration | Journey 3: Custom Extension Authoring | Jordan (Plugin Author) | FR-01, FR-05, NFR-PBT |
| **US-06** | Security & Resiliency Hardening | Journey 4: Enterprise & Platform Guard | Morgan (Security Admin) | NFR-SEC, NFR-RES, NFR-PBT |

---

## Journey 1: Interactive Terminal Developer

### US-01: Interactive CLI Agent Session
**As a** CLI Practitioner (Alex),  
**I want** to launch an interactive agent session from the command line using `dsh` or `python -m dsh`,  
**So that** I can collaborate with the DeepSeek LLM to solve coding tasks with real-time streaming output.

#### Acceptance Criteria (Gherkin Scenarios):
```gherkin
Scenario: Starting a new interactive CLI session
  Given a valid DEEPSEEK_API_KEY environment variable is configured
  When the user runs `dsh` or `python -m dsh` in the workspace directory
  Then a new session is initialized and assigned a unique UUID
  And the interactive prompt displays welcoming the user and showing active profile "cli"

Scenario: Streaming model response in real time
  Given an active interactive CLI session
  When the user types a prompt "Explain the project architecture"
  Then the system compiles the dynamic system prompt
  And streams the model tokens in real-time to standard output
  And closes the turn with a successful turn/end event

Scenario: Handling missing API key gracefully
  Given the DEEPSEEK_API_KEY environment variable is unset
  When the user launches `dsh`
  Then the application exits cleanly with a helpful error message instructing how to set DEEPSEEK_API_KEY
  And does not leak internal stack traces (SECURITY-08)
```

---

### US-02: Scoped File System & Shell Tool Execution
**As a** CLI Practitioner (Alex),  
**I want** the agent to safely read, modify files, and run terminal commands in my workspace,  
**So that** the agent can execute real implementation tasks autonomously with guardrails.

#### Acceptance Criteria (Gherkin Scenarios):
```gherkin
Scenario: Agent executes file read and edit tools
  Given the agent determines it needs to read `src/main.py`
  When the agent emits a `view_file` tool call with path `src/main.py`
  Then the tool executor validates the path is within workspace boundaries
  And returns the file content to the agent loop
  And the tool call and result are recorded as durable events in the session log

Scenario: Agent executes shell command with timeout protection
  Given the agent invokes `run_command` with `pytest`
  When the command runs
  Then standard output is captured and returned to the model
  And if the process exceeds the configured timeout, the entire process tree is terminated gracefully (RES-02)

Scenario: Blocking unauthorized path traversal
  Given the agent attempts to access `/etc/passwd` or outside the workspace root
  When the tool parameter validator inspects the requested path
  Then the tool call is rejected with a permission error (SECURITY-05)
  And the agent is informed of the path boundary constraint
```

---

## Journey 2: SDK & Embedded Integration

### US-03: Durable Session Event Store & Replay
**As an** AI Platform Engineer (Taylor),  
**I want** all turn interactions, messages, tool calls, and results to be stored in an append-only event log,  
**So that** sessions can be replayed, inspected, audited, and resumed deterministically.

#### Acceptance Criteria (Gherkin Scenarios):
```gherkin
Scenario: Appending session events monotonically
  Given an active session with ID "sess-123"
  When turns and tool calls occur
  Then each event is appended with an incremental sequence number and ISO timestamp
  And is persisted atomically to `sessions/sess-123.jsonl` (RES-03)

Scenario: Replaying past session history
  Given an existing session file with 10 recorded events
  When the SDK loads the session using `Session.load("sess-123")`
  Then all 10 events are deserialized with exact schema fidelity
  And round-trip property tests verify `deserialize(serialize(event)) == event` (PBT-01)
```

---

### US-04: Programmatic SDK Turn Orchestration
**As an** AI Platform Engineer (Taylor),  
**I want** to embed the DeepSeek Harness kernel into a Python service using clean async APIs,  
**So that** I can trigger automated agent turns from external APIs, webhooks, or background jobs.

#### Acceptance Criteria (Gherkin Scenarios):
```gherkin
Scenario: Programmatically executing an agent turn
  Given a configured Python `Context` with LLM and Tool services registered
  When the caller awaits `context.agent_loop.start_turn(agent, "Refactor module X")`
  Then the agent loop processes input, invokes LLM streaming, executes needed tools
  And returns a structured `TurnResult` containing total steps, tokens used, and completion status
```

---

## Journey 3: Custom Extension Authoring

### US-05: Custom Plugin & Tool Registration
**As a** Plugin Author (Jordan),  
**I want** to define custom tools using Pydantic models and register them with Cordis-like lifecycle hooks,  
**So that** I can expand agent capabilities with type safety and automatic schema generation.

#### Acceptance Criteria (Gherkin Scenarios):
```gherkin
Scenario: Registering a custom Pydantic-based tool
  Given a tool definition class extending `BaseTool` with Pydantic arguments `SearchArgs`
  When the plugin is mounted onto the Cordis `Context`
  Then the tool schema is automatically derived and added to the LLM system prompt
  And tool invocations automatically parse and validate input parameters (SECURITY-05)

Scenario: Plugin unmounting cleans up registered tools
  Given a mounted plugin that registered tool `custom_query`
  When the plugin scope is disposed or unmounted
  Then `custom_query` is automatically removed from active tool registries without side effects (FR-01.3)
```

---

## Journey 4: Enterprise & Platform Guard

### US-06: Security & Resiliency Hardening
**As a** Security Administrator (Morgan),  
**I want** all credentials to be masked, logs structured, and network requests retried with exponential backoff,  
**So that** the application is safe, robust against transient errors, and enterprise compliant.

#### Acceptance Criteria (Gherkin Scenarios):
```gherkin
Scenario: Structured logging with automated secret masking
  Given an LLM request containing API authorization headers or sensitive tokens
  When the logging subsystem outputs log records
  Then all API keys and bearer tokens are replaced with `***MASKED***` (SECURITY-03)
  And logs include standard correlation ID, timestamp, and log level

Scenario: Resilient LLM retry on connection drop
  Given the DeepSeek API endpoint experiences a temporary HTTP 503 or network disconnect
  When the LLM adapter is streaming tokens
  Then the adapter retries with exponential backoff and jitter up to max retry limit (RES-01)
  And seamlessly resumes the stream without failing the agent turn
```
