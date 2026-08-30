"""Исключения инфраструктурного слоя."""


class PoolNotConfiguredError(RuntimeError):
    """Пул соединений не сконфигурирован."""


class OfmPoolNotConfiguredError(PoolNotConfiguredError):
    """Пул соединений OFM (Oracle) не сконфигурирован."""


class RedisPoolNotConfiguredError(PoolNotConfiguredError):
    """Пул соединений Redis не сконфигурирован."""
