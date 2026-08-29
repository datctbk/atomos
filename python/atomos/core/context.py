"""Context container and Dependency Injection mechanism for Atomos."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Coroutine
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class Disposable(Protocol):
    """Protocol for reversible registrations in Context."""

    def dispose(self) -> None:
        """Unbind or clean up the registered resource."""
        ...


class CallbackDisposable:
    """Disposable wrapper executing a provided cleanup callback."""

    def __init__(self, cleanup: Callable[[], None]) -> None:
        self._cleanup = cleanup
        self._disposed = False

    def dispose(self) -> None:
        if not self._disposed:
            self._disposed = True
            self._cleanup()


class Context:
    """Cordis-equivalent Dependency Injection and Plugin Context for Atomos."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._listeners: dict[str, list[Callable[..., Any]]] = {}
        self._waterfalls: dict[str, list[Callable[..., Any]]] = {}

    def _to_key(self, name: str | type[Any]) -> str:
        return name if isinstance(name, str) else f"{name.__module__}.{name.__qualname__}"

    def provide(self, name: str | type[Any], service: Any) -> Disposable:
        """Register a service in the context."""
        key = self._to_key(name)
        self._services[key] = service

        def cleanup() -> None:
            if self._services.get(key) is service:
                del self._services[key]

        return CallbackDisposable(cleanup)

    def get(self, name: str | type[T], default: Any = None) -> Any:
        """Retrieve a service from the context."""
        key = self._to_key(name)
        return self._services.get(key, default)

    def has(self, name: str | type[Any]) -> bool:
        """Check if a service is registered in the context."""
        key = self._to_key(name)
        return key in self._services

    def dispose(self) -> None:
        """Dispose all registered services and listeners."""
        self._services.clear()
        self._listeners.clear()
        self._waterfalls.clear()

    def on(self, event: str, handler: Callable[..., Any]) -> Disposable:
        """Register an asynchronous or synchronous event listener."""
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
        """Register a waterfall middleware interceptor."""
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
        """Emit an event sequentially to all registered listeners."""
        handlers = list(self._listeners.get(event, []))
        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                res = handler(*args, **kwargs)
                if inspect.isawaitable(res):
                    await res

    async def pipe(self, event: str, initial_value: Any) -> Any:
        """Execute waterfall middleware pipeline."""
        handlers = list(self._waterfalls.get(event, []))

        async def dispatch(index: int, value: Any) -> Any:
            if index >= len(handlers):
                return value
            handler = handlers[index]

            async def next_step() -> Any:
                return await dispatch(index + 1, value)

            return await handler(value, next_step)

        return await dispatch(0, initial_value)
