from collections.abc import Callable, Coroutine
from typing import Any

import pytest

from atomos.core.events import EventBus


@pytest.mark.asyncio
async def test_event_bus_subscribe_emit_dispose() -> None:
    bus = EventBus()
    calls: list[str] = []

    async def h1(data: Any) -> None:
        calls.append(f"h1:{data}")

    async def h2(data: Any) -> None:
        calls.append(f"h2:{data}")

    d1 = bus.subscribe("evt", h1)
    bus.subscribe("evt", h2)

    await bus.emit("evt", 42)
    assert calls == ["h1:42", "h2:42"]

    d1.dispose()
    await bus.emit("evt", 99)
    assert calls == ["h1:42", "h2:42", "h2:99"]


@pytest.mark.asyncio
async def test_event_bus_waterfall_transformation() -> None:
    bus = EventBus()

    async def add_prefix(val: int, next_fn: Callable[[], Coroutine[Any, Any, int]]) -> int:
        res = await next_fn()
        return res + 10

    async def multiplier(val: int, next_fn: Callable[[], Coroutine[Any, Any, int]]) -> int:
        return val * 2

    bus.waterfall("compute", add_prefix)
    bus.waterfall("compute", multiplier)

    res = await bus.pipe("compute", 5)
    assert res == 20
