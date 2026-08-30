"""Тесты WorkRegistry: регистрация и поиск обработчиков."""

import pytest

from app.core.services.entrypoints.registry import WorkRegistry


def test_add_and_handler() -> None:
    registry = WorkRegistry()

    @registry.add("report:profile")
    async def handler() -> None: ...

    assert registry.handler("report:profile") is handler


def test_handler_unknown_route() -> None:
    registry = WorkRegistry()

    @registry.add("report:profile")
    async def handler() -> None: ...

    with pytest.raises(RuntimeError, match="report:unknown"):
        registry.handler("report:unknown")


def test_handler_unknown_route_lists_registered() -> None:
    registry = WorkRegistry()

    @registry.add("report:profile")
    async def handler() -> None: ...

    with pytest.raises(RuntimeError, match="report:profile"):
        registry.handler("report:unknown")


def test_handler_empty_registry() -> None:
    registry = WorkRegistry()

    with pytest.raises(RuntimeError, match="<нет>"):
        registry.handler("anything")
