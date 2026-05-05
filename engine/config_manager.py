from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Read and write local JSON configuration files used by the engine."""

    def __init__(self, config_dir: str | Path) -> None:
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def read_json(self, file_name: str, default: Any | None = None) -> Any:
        path = self.config_dir / file_name
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def write_json(self, file_name: str, payload: Any) -> Path:
        path = self.config_dir / file_name
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        return path
