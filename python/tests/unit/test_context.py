from collections.abc import Callable, Coroutine
from typing import Any

import pytest

from atomos.core.context import Context


def test_context_service_registration_and_disposal() -> None:
    ctx = Context()
    dummy_service = {"version": "1.0.0"}

    token = ctx.provide("my_service", dummy_service)
    assert ctx.get("my_service") == dummy_service
    assert ctx.get("unknown_service") is None
    assert ctx.get("unknown_service", default="fallback") == "fallback"

    token.dispose()
    assert ctx.get("my_service") is None


@pytest.mark.asyncio
async def test_context_event_listeners() -> None:
    ctx = Context()
    received: list[str] = []

    async def async_handler(msg: str) -> None:
        received.append(f"async:{msg}")

    def sync_handler(msg: str) -> None:
        received.append(f"sync:{msg}")

    t1 = ctx.on("test/event", async_handler)
    ctx.on("test/event", sync_handler)

    await ctx.emit("test/event", "hello")
    assert received == ["async:hello", "sync:hello"]

    t1.dispose()
    await ctx.emit("test/event", "world")
    assert received == ["async:hello", "sync:hello", "sync:world"]


@pytest.mark.asyncio
async def test_context_waterfall_pipeline() -> None:
    ctx = Context()

    async def middleware_1(val: str, next_fn: Callable[[], Coroutine[Any, Any, Any]]) -> str:
        res = await next_fn()
        return f"[M1_START]{res}[M1_END]"

    async def middleware_2(val: str, next_fn: Callable[[], Coroutine[Any, Any, Any]]) -> str:
        return f"[M2]{val}"

    ctx.waterfall("process", middleware_1)
    ctx.waterfall("process", middleware_2)

    result = await ctx.pipe("process", "DATA")
    assert result == "[M1_START][M2]DATA[M1_END]"
