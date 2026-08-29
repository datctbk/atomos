# User Personas

This document defines the key user archetypes for the Python reimplementation of DeepSeek Harness (`dsh`).

---

## Persona 1: Alex — Python CLI Practitioner & AI Developer
- **Role**: Software engineer using `dsh` from the command line for day-to-day coding, interactive pair programming, and repository automation.
- **Key Needs**:
  - Fast, responsive CLI startup (`dsh` or `python -m dsh`).
  - Real-time streaming output of LLM responses and tool execution steps.
  - Safe, automatic file manipulation and terminal command execution with user confirmation.
  - Seamless multi-turn session persistence and recovery.
- **Pain Points**:
  - Clunky configuration setups or unhandled stream disconnects.
  - Opaque tool execution that alters files unexpectedly.

---

## Persona 2: Taylor — AI Platform Engineer & SDK Integrator
- **Role**: Backend engineer integrating DeepSeek Harness into backend services, automated CI pipelines, and internal tools.
- **Key Needs**:
  - Clean, idiomatic Python async API (`from dsh import Context, AgentLoop, Session`).
  - Deterministic event sourcing log (`SessionEvent`) for telemetry and auditing.
  - Programmatic session creation, turn dispatching, and structured tool interception.
  - Clean separation between kernel logic and application launchers.
- **Pain Points**:
  - Complex dependency graphs that make embedding difficult.
  - Inability to intercept or rewrite messages/tools in flight.

---

## Persona 3: Jordan — Custom Plugin & Tool Author
- **Role**: Specialist developer extending `dsh` with domain-specific tools (e.g., custom database inspectors, MCP servers, sandbox runtimes).
- **Key Needs**:
  - Simple, schema-driven tool definition syntax using Pydantic models.
  - Reversible plugin registration with Cordis-equivalent dependency injection.
  - Lifecycle hooks (`tools/pre-execute`, `tools/post-execute`) for safety checks and formatting.
- **Pain Points**:
  - Rigid tool interfaces that require boilerplate or manual JSON schema authoring.
  - Leaky abstractions where tool errors crash the entire agent loop.

---

## Persona 4: Morgan — Platform & Security Administrator
- **Role**: Security engineer ensuring compliance, access control, and resilience across developer environments.
- **Key Needs**:
  - Strict enforcement of security constraints (`SECURITY-01` through `SECURITY-08`).
  - Automatic masking of API credentials and zero hardcoded secrets.
  - Strict subprocess timeouts and process isolation preventing zombie execution.
  - Structured audit logs tracking all actions and session events.
- **Pain Points**:
  - Unsanitized error messages exposing internal system internals to LLMs.
  - Unbounded background processes consuming excessive host resources.
