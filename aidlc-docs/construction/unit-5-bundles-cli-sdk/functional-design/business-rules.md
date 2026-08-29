# Unit 5 Business Rules & Validation: Bundles, CLI & SDK

This document specifies the configuration precedence rules, CLI binary alias registrations, and SDK lifecycle management.

---

## 1. Core Invariants & Business Rules

### BR-BOOT-01: Configuration Precedence Hierarchy
- **Rule**: Configuration parameters resolve in strict priority order:
  $$\text{CLI Flags} > \text{Environment Variables} > \text{Profile / Defaults}$$
- **Example**: If `--local-url` is passed on CLI, it overrides `ATOMOS_LOCAL_LLM_URL` and `http://localhost:11434/v1`.

### BR-BOOT-02: Dual Binary Entrypoint Compatibility
- **Rule**: The package manifest MUST expose both `atomos` (primary command) and `atimos` (command alias) pointing to `atomos.cli.main:app`.
- **Validation**: Executing either `atomos --help` or `atimos --help` invokes the same Typer application.

### BR-BOOT-03: Zero API Key Requirement for `--local` Mode
- **Rule**: When `--local` or `-l` is enabled, the CLI and SDK MUST NOT require or validate `DEEPSEEK_API_KEY` or `OPENAI_API_KEY`.

### BR-BOOT-04: Graceful SDK Context Disposal
- **Rule**: Exiting an `AtomosClient` async context manager MUST automatically dispose mounted bundle tokens, close open file handles, and finalize open session streams.

---

## 2. Testable Properties for Property-Based Testing (PBT-01)

| Property Name | Category | Description |
|---|---|---|
| `prop_profile_config_precedence` | **Configuration Invariant** | CLI options always strictly override environment variable fallbacks across randomized parameter inputs. |
| `prop_sdk_lifecycle_cleanup` | **Resource Management** | Entering and exiting `AtomosClient` repeatedly leaves zero open session file descriptors or unreleased context bindings. |
