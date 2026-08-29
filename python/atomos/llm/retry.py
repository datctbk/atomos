"""Resilience retry mechanism with exponential backoff and full jitter (RES-01)."""

from __future__ import annotations

import asyncio
import logging
import random
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
    """Wraps an async generator stream with exponential backoff and full jitter retry."""
    attempt = 0
    while True:
        try:
            async for item in generator_factory():
                yield item
            return
        except Exception as exc:
            attempt += 1
            if attempt > max_retries:
                logger.error("LLM stream failed after %d retries: %s", max_retries, exc)
                raise

            # Full Jitter backoff algorithm: random between 0 and min(max_delay, base * 2^(attempt-1))
            upper_bound = min(max_delay, base_delay * (2 ** (attempt - 1)))
            sleep_time = random.uniform(0, upper_bound)
            logger.warning(
                "LLM streaming exception (%s). Retrying attempt %d/%d after %.2fs...",
                exc,
                attempt,
                max_retries,
                sleep_time,
            )
            await asyncio.sleep(sleep_time)
