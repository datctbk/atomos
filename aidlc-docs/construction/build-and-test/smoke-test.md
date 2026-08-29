# Smoke Test & Integration Verification: Atomos

This document provides smoke test verification procedures for CLI execution, local LLM offline runs, and the Python SDK.

---

## 1. CLI Smoke Test (Help & Commands)

```bash
# Verify 'atomos' command
uv run atomos --help

# Verify 'atimos' command alias
uv run atimos --help
```

---

## 2. Programmatic SDK Integration Smoke Test

```python
import asyncio
from atomos.sdk import AtomosClient

async def smoke_test():
    async with AtomosClient(workspace=".", is_local=True) as client:
        print("[AtomosClient] Successfully bootstrapped context, session store, and agent loop.")

if __name__ == "__main__":
    asyncio.run(smoke_test())
```

---

## 3. Local Model Offline Invocation Smoke Test

```bash
# Connect to local Ollama runner on port 11434
atomos --local --model qwen2.5-coder "List the files in the current workspace"
```
