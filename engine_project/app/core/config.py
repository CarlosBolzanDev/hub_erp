from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class RuntimeConfig:
    runtime_name: str = "Python Runtime Engine"
    selected_scripts: list[str] = field(default_factory=list)
    log_level: str = "INFO"
    theme: str = "default"
    startup: dict[str, Any] = field(default_factory=lambda: {"autoload_selected": False})


class ConfigManager:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._config = RuntimeConfig()

    @property
    def data(self) -> RuntimeConfig:
        return self._config

    def load(self) -> RuntimeConfig:
        if not self._config_path.exists():
            self.save()
            return self._config
        with self._config_path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        self._config = RuntimeConfig(
            runtime_name=raw.get("runtime_name", self._config.runtime_name),
            selected_scripts=list(raw.get("selected_scripts", [])),
            log_level=raw.get("log_level", self._config.log_level),
            theme=raw.get("theme", self._config.theme),
            startup=raw.get("startup", self._config.startup),
        )
        return self._config

    def save(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with self._config_path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self._config), fh, indent=2, ensure_ascii=False)
