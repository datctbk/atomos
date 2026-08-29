# Unit 5 Business Logic Model: Bundles, CLI & SDK

This document describes the application bootstrapping flow, bundle mounting lifecycle, Typer/Rich CLI interface, and the async Python SDK usage.

---

## 1. Bootstrapping Flowchart

```mermaid
flowchart TD
    Invocation["CLI / SDK Invocation<br/>(atomos / AtomosClient)"]
    ResolveConfig["Resolve Options & CLI Flags<br/>(--local, --model, --workspace)"]
    CreateProfile["Construct Profile"]
    MountCore["Mount CoreBundle<br/>(EventBus, SessionStore, RedactionFilter)"]
    MountTools["Mount ToolsBundle<br/>(PathSandbox, FS Tools, Shell Tool)"]
    MountLLM["Mount LLMBundle<br/>(DeepSeekAdapter / Local OpenAIAdapter)"]
    AssembleLoop["Instantiate AgentLoop(context, session, adapter, registry)"]
    DispatchAction{"Mode?"}
    InteractiveCLI["Run Rich Interactive REPL Loop"]
    SingleTurnCLI["Stream Single-Turn Prompt & Exit"]
    SDKRunner["Yield Tokens via Async Iterator"]

    Invocation --> ResolveConfig --> CreateProfile --> MountCore --> MountTools --> MountLLM --> AssembleLoop --> DispatchAction
    DispatchAction -- "Interactive CLI" --> InteractiveCLI
    DispatchAction -- "One-off CLI prompt" --> SingleTurnCLI
    DispatchAction -- "SDK Client" --> SDKRunner
```

---

## 2. CLI Command Structure

### 2.1 Interactive Terminal Chat
```bash
# Default Cloud execution (DeepSeek / OpenAI)
atomos

# Local LLM execution (Ollama at http://localhost:11434/v1)
atomos --local
atomos -l --model qwen2.5-coder

# Execute with specific workspace root
atomos --workspace ./my-project "Inspect the test suite"

# Command alias
atimos --local
```

---

## 3. Programmatic SDK Usage

```python
import asyncio
from atomos.sdk import AtomosClient

async def main():
    # Connect with local runner
    async with AtomosClient(workspace=".", is_local=True, model="deepseek-r1") as client:
        async for token in client.chat("Analyze the project structure"):
            print(token, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```
