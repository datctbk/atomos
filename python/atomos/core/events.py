"""EventBus implementation for Atomos."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Coroutine
from typing import Any

from atomos.core.context import CallbackDisposable, Disposable


class EventBus:
    """EventBus managing broadcast and waterfall handlers independently."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = {}
        self._waterfalls: dict[str, list[Callable[..., Any]]] = {}

    def subscribe(self, event: str, handler: Callable[..., Any]) -> Disposable:
        """Subscribe a listener to an event."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)

        def cleanup() -> None:
            if event in self._listeners and handler in self._listeners[event]:
                self._listeners[event].remove(handler)
                if not self._listeners[event]:
                    del self._listeners[event]

        return CallbackDisposable(cleanup)

    def waterfall(
        self,
        event: str,
        handler: Callable[[Any, Callable[[], Coroutine[Any, Any, Any]]], Coroutine[Any, Any, Any]],
    ) -> Disposable:
        """Register a waterfall interceptor."""
        if event not in self._waterfalls:
            self._waterfalls[event] = []
        self._waterfalls[event].append(handler)

        def cleanup() -> None:
            if event in self._waterfalls and handler in self._waterfalls[event]:
                self._waterfalls[event].remove(handler)
                if not self._waterfalls[event]:
                    del self._waterfalls[event]

        return CallbackDisposable(cleanup)

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Publish broadcast event sequentially."""
        handlers = list(self._listeners.get(event, []))
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                res = handler(*args, **kwargs)
                if inspect.isawaitable(res):
                    await res

    async def pipe(self, event: str, initial_value: Any) -> Any:
        """Run waterfall pipeline chaining handlers with await next()."""
        handlers = list(self._waterfalls.get(event, []))

        async def dispatch(index: int, value: Any) -> Any:
            if index >= len(handlers):
                return value
            handler = handlers[index]

            async def next_step() -> Any:
                return await dispatch(index + 1, value)

            return await handler(value, next_step)

        return await dispatch(0, initial_value)
