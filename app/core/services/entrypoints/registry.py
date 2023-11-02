from collections import UserDict
from collections.abc import Callable
from typing import Any


class WorkRegistry(UserDict):
    def add(self, route_url: str) -> Callable[..., Any]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.data[route_url] = func
            return func

        return decorator
