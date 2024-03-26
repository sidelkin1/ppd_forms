from collections.abc import Callable

import structlog

ProcessorType = Callable[
    [
        structlog.types.WrappedLogger,
        str,
        structlog.types.EventDict,
    ],
    str | bytes,
]


def get_render_processor(
    render_json_logs: bool = False, colors: bool = True
) -> ProcessorType:
    if render_json_logs:
        return structlog.processors.JSONRenderer()
    return structlog.dev.ConsoleRenderer(colors=colors)
