"""Persistent JSON configuration for the NF-e organizer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    """Application paths persisted between GUI sessions."""

    entrada: str
    saida: str

    @classmethod
    def default(cls, base_dir: Path) -> "AppConfig":
        return cls(
            entrada=str(base_dir / "entrada"),
            saida=str(base_dir / "processados"),
        )


class ConfigManager:
    """Load and save user-selected folders in JSON format."""

    def __init__(self, config_path: Path, base_dir: Path) -> None:
        self.config_path = config_path
        self.base_dir = base_dir

    def load(self) -> AppConfig:
        default = AppConfig.default(self.base_dir)
        if not self.config_path.exists():
            self.save(default)
            return default

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default

        return AppConfig(
            entrada=str(data.get("entrada") or default.entrada),
            saida=str(data.get("saida") or default.saida),
        )

    def save(self, config: AppConfig) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"entrada": config.entrada, "saida": config.saida}
        self.config_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
