from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from utils.file_utils import sorted_python_files
from utils.validation import validate_script_file


@dataclass(frozen=True)
class ScriptInfo:
    name: str
    path: Path
    valid: bool
    message: str


class ScriptLoader:
    """Discover runnable Python scripts in the configured Scripts folder."""

    def __init__(self, scripts_dir: Path, logger: logging.Logger) -> None:
        self.scripts_dir = scripts_dir
        self.logger = logger

    def discover(self) -> list[ScriptInfo]:
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        scripts: list[ScriptInfo] = []
        for path in sorted_python_files(self.scripts_dir):
            valid, message = validate_script_file(path)
            info = ScriptInfo(name=path.name, path=path, valid=valid, message=message)
            scripts.append(info)
            if valid:
                self.logger.info("Script encontrado: %s", path.name)
            else:
                self.logger.warning("%s %s", path.name, message)
        self.logger.info("Varredura concluída: %d script(s) Python encontrado(s).", len(scripts))
        return scripts

    def valid_scripts(self) -> list[ScriptInfo]:
        return [script for script in self.discover() if script.valid]
