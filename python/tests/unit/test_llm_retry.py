from collections.abc import AsyncIterator

import pytest

from atomos.llm.retry import retry_async_stream


@pytest.mark.asyncio
async def test_retry_async_stream_success_first_try() -> None:
    async def sample_gen() -> AsyncIterator[int]:
        for i in range(3):
            yield i

    items: list[int] = []
    async for val in retry_async_stream(sample_gen, max_retries=2, base_delay=0.01):
        items.append(val)

    assert items == [0, 1, 2]


@pytest.mark.asyncio
async def test_retry_async_stream_recovers_after_failure() -> None:
    attempts = 0

    async def flaky_gen() -> AsyncIterator[str]:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ConnectionResetError("Connection lost")
        yield "recovered"

    items: list[str] = []
    async for val in retry_async_stream(flaky_gen, max_retries=2, base_delay=0.01):
        items.append(val)

    assert attempts == 2
    assert items == ["recovered"]


@pytest.mark.asyncio
async def test_retry_async_stream_raises_after_max_retries() -> None:
    async def always_failing_gen() -> AsyncIterator[str]:
        raise TimeoutError("Endpoint timed out")
        yield "never"

    with pytest.raises(TimeoutError, match="Endpoint timed out"):
        async for _ in retry_async_stream(always_failing_gen, max_retries=2, base_delay=0.01):
            pass
