from __future__ import annotations

import logging
from pathlib import Path

from core.config_manager import EngineManifest, RegisteredScript
from core.runtime_bridge import RuntimePaths
from utils.file_utils import resolve_registered_path
from utils.validation import validate_script_file


class ScriptLoader:
    """Manage scripts registered by explicit file path; no fixed script folder is assumed."""

    def __init__(self, runtime_paths: RuntimePaths, logger: logging.Logger) -> None:
        self.runtime_paths = runtime_paths
        self.logger = logger

    def add_script(self, manifest: EngineManifest, file_path: Path) -> RegisteredScript:
        resolved = file_path.expanduser().resolve(strict=False)
        if any(str(self.resolve_path(script)).casefold() == str(resolved).casefold() for script in manifest.scripts):
            raise ValueError("Este script já está cadastrado no manifesto.")

        script = RegisteredScript.create(resolved)
        self.validate_script(script)
        manifest.scripts.append(script)
        self.logger.info("Script adicionado: %s (%s)", script.display_name, script.path)
        return script

    def remove_script(self, manifest: EngineManifest, script_id: str) -> RegisteredScript | None:
        for index, script in enumerate(manifest.scripts):
            if script.id == script_id:
                removed = manifest.scripts.pop(index)
                self.logger.info("Script removido: %s (%s)", removed.display_name, removed.path)
                return removed
        return None

    def validate_all(self, manifest: EngineManifest) -> list[RegisteredScript]:
        for script in manifest.scripts:
            self.validate_script(script)
        self.logger.info("Manifesto carregado: %d script(s) cadastrado(s).", len(manifest.scripts))
        return manifest.scripts

    def validate_script(self, script: RegisteredScript) -> RegisteredScript:
        path = Path(self.resolve_path(script))
        valid, message = validate_script_file(path)
        script.validation_status = message if valid else f"Inválido: {message}"
        if valid:
            self.logger.info("Script validado: %s (%s)", script.display_name, path)
        else:
            self.logger.warning("Script inválido: %s (%s) - %s", script.display_name, path, message)
        return script

    def enabled_scripts(self, manifest: EngineManifest) -> list[RegisteredScript]:
        return [script for script in manifest.scripts if script.enabled]

    def resolve_path(self, script: RegisteredScript) -> str:
        return str(resolve_registered_path(script.path, self.runtime_paths.base_dir))
