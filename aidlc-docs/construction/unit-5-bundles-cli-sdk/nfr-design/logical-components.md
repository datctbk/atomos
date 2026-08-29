# Unit 5 Logical Components: Bundles, CLI & SDK

This document specifies the logical component structure and interaction model for Unit 5.

---

## 1. Component Architecture Diagram

```mermaid
graph TD
    CLI["Typer CLI App<br/>(atomos / atimos)"]
    SDK["AtomosClient<br/>(atomos.sdk)"]
    Profile["Profile<br/>(atomos.boot.profile)"]
    Bundles["Bundles<br/>(Core, Tools, LLM)"]
    DIContext["Context (DI & Events)"]
    Agent["AgentLoop"]

    CLI -->|instantiates| Profile
    SDK -->|instantiates| Profile
    Profile -->|applies| Bundles
    Bundles -->|binds| DIContext
    Profile -->|constructs| Agent
```

---

## 2. Logical Components Breakdown

### 2.1 `Profile` (`atomos.boot.profile`)
- **Type**: Bootstrapper Component
- **Responsibilities**:
  - Encapsulates configuration and instantiates the full object graph (Context, SessionStore, ToolRegistry, LLMAdapter, AgentLoop).

### 2.2 `BaseBundle` (`atomos.boot.bundles.base`)
- **Type**: Extension Architecture
- **Responsibilities**:
  - `CoreBundle`: Configures session storage and event filters.
  - `ToolsBundle`: Mounts filesystem and shell tools into registry.
  - `LLMBundle`: Configures cloud or local LLM adapters.

### 2.3 `CLIApp` (`atomos.cli.main`)
- **Type**: User Interface
- **Responsibilities**:
  - Provides `atomos` command (and alias `atimos`).
  - Flags: `--local`, `--model`, `--workspace`, `--session`.
  - Integrates Rich Live markdown streaming.

### 2.4 `AtomosClient` (`atomos.sdk.client`)
- **Type**: Programmatic API
- **Responsibilities**:
  - Async context manager exposing `async def chat(prompt) -> AsyncIterator[str]`.
