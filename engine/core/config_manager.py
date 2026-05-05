from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from utils.file_utils import ensure_directory


@dataclass
class RegisteredScript:
    """Script registered manually by the developer through the engine UI."""

    id: str
    display_name: str
    path: str
    enabled: bool = True
    validation_status: str = "Não validado"
    last_execution: str = "Nunca"

    @classmethod
    def create(cls, path: Path, display_name: str | None = None) -> "RegisteredScript":
        return cls(id=uuid4().hex, display_name=display_name or path.stem, path=str(path))


@dataclass
class EngineManifest:
    scripts: list[RegisteredScript] = field(default_factory=list)
    execution_options: dict[str, Any] = field(default_factory=lambda: {"stop_on_error": False})
    default_arguments: str = ""


class ConfigManager:
    """Read and write the local JSON manifest used by the engine."""

    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        ensure_directory(manifest_path.parent)

    def load(self) -> EngineManifest:
        if not self.manifest_path.exists():
            manifest = EngineManifest()
            self.save(manifest)
            return manifest

        try:
            raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return EngineManifest()

        scripts = []
        for item in raw.get("scripts", []):
            if not isinstance(item, dict):
                continue
            path = str(item.get("path", "")).strip()
            if not path:
                continue
            scripts.append(
                RegisteredScript(
                    id=str(item.get("id") or uuid4().hex),
                    display_name=str(item.get("display_name") or Path(path).stem),
                    path=path,
                    enabled=bool(item.get("enabled", True)),
                    validation_status=str(item.get("validation_status", "Não validado")),
                    last_execution=str(item.get("last_execution", "Nunca")),
                )
            )

        return EngineManifest(
            scripts=scripts,
            execution_options=dict(raw.get("execution_options", {"stop_on_error": False})),
            default_arguments=str(raw.get("default_arguments", "")),
        )

    def save(self, manifest: EngineManifest) -> None:
        payload = asdict(manifest)
        self.manifest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
