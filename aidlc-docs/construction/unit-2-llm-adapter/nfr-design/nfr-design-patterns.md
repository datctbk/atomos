# Unit 2 NFR Design Patterns: LLM Adapter & Streaming Engine

This document details the concrete implementation patterns for full jitter backoff retry (`RES-01`), SSE line buffer parsing, and local model runner integration.

---

## 1. Resilience Patterns: Full Jitter Exponential Backoff (`RES-01`)

```python
import asyncio
import random
import logging
from collections.abc import AsyncIterator, Callable
from typing import TypeVar

T = TypeVar("T")
logger = logging.getLogger("atomos.llm")

async def retry_async_stream(
    generator_factory: Callable[[], AsyncIterator[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
) -> AsyncIterator[T]:
    """Wraps an async generator with exponential backoff and full jitter retry."""
    attempt = 0
    while True:
        try:
            async for item in generator_factory():
                yield item
            return
        except Exception as exc:
            attempt += 1
            if attempt > max_retries:
                logger.error(f"Stream failed after {max_retries} retries: {exc}")
                raise exc

            # Full Jitter: random between 0 and min(max_delay, base * 2^attempt)
            sleep_time = random.uniform(0, min(max_delay, base_delay * (2 ** (attempt - 1))))
            logger.warning(
                f"LLM stream error ({exc}). Retrying attempt {attempt}/{max_retries} "
                f"after {sleep_time:.2f}s..."
            )
            await asyncio.sleep(sleep_time)
```

---

## 2. Local Model Runner Integration Pattern

```python
class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI-compatible streaming adapter supporting both Cloud (OpenAI) and Local (Ollama, LMStudio, vLLM)."""

    def __init__(
        self,
        model: str = "deepseek-r1",
        api_key: str | None = None,
        base_url: str | None = None,
        is_local: bool = False,
    ) -> None:
        self.model = model
        self.is_local = is_local
        if is_local:
            # Default to local Ollama/LMStudio endpoint without requiring API key
            self.base_url = base_url or os.environ.get("ATOMOS_LOCAL_LLM_URL", "http://localhost:11434/v1")
            self.api_key = api_key or "local-no-key"
        else:
            self.base_url = base_url or "https://api.openai.com/v1"
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
```
