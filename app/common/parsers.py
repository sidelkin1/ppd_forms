from pathlib import Path
from typing import Any

import yaml


def read_config(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_config_map(path: Path, key: str) -> dict[str, Any]:
    """Читает YAML-конфиг и возвращает его items словарём по ключу.

    Например, для ``tables.yaml`` с ключом ``path`` —
    ``{"report": {...}, "profile": {...}, ...}``.
    """
    config = read_config(path)
    return {item[key]: item for item in config["items"]}
