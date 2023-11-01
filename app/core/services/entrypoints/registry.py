from collections import UserDict
from typing import Callable


class WorkRegistry(UserDict):
    def add(self, route_url: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.data[route_url] = func
            return func

        return decorator
