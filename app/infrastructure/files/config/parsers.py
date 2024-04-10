from pathlib import Path
from typing import Any

import yaml


def read_config(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
