from collections import UserDict
from collections.abc import Callable
from typing import Any


class WorkRegistry(UserDict):
    def add(self, route_url: str) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.data[route_url] = func
            return func

        return decorator

    def handler(self, route_url: str) -> Callable[..., Any]:
        """Возвращает обработчик маршрута или падает с понятной ошибкой."""
        try:
            return self.data[route_url]
        except KeyError:
            registered = ", ".join(sorted(self.data)) or "<нет>"
            raise RuntimeError(
                f"Неизвестный маршрут: {route_url!r}. "
                f"Зарегистрированы: {registered}"
            ) from None
