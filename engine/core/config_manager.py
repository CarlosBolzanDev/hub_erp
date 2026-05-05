from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from utils.file_utils import ensure_directory


@dataclass
class EngineSettings:
    scripts_folder: str = "Scripts"
    selected_scripts: list[str] = field(default_factory=list)
    execution_options: dict[str, Any] = field(default_factory=lambda: {"stop_on_error": False})
    default_arguments: str = ""


class ConfigManager:
    """Read and write the local JSON engine configuration."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        ensure_directory(config_path.parent)

    def load(self) -> EngineSettings:
        if not self.config_path.exists():
            settings = EngineSettings()
            self.save(settings)
            return settings

        try:
            raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return EngineSettings()

        return EngineSettings(
            scripts_folder=str(raw.get("scripts_folder", "Scripts")),
            selected_scripts=list(raw.get("selected_scripts", [])),
            execution_options=dict(raw.get("execution_options", {"stop_on_error": False})),
            default_arguments=str(raw.get("default_arguments", "")),
        )

    def save(self, settings: EngineSettings) -> None:
        payload = asdict(settings)
        self.config_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
