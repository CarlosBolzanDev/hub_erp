from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from utils.file_utils import ensure_directory, normalize_path, unique_existing_paths


@dataclass(frozen=True)
class RuntimePaths:
    base_dir: Path
    embedded_python_dir: Path
    libs_dir: Path
    config_dir: Path
    logs_dir: Path


class RuntimeBridge:
    """Prepare paths so the engine behaves like a portable embedded runtime."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = normalize_path(base_dir or Path(__file__).resolve().parents[1])
        self.paths = RuntimePaths(
            base_dir=self.base_dir,
            embedded_python_dir=self.base_dir / "python",
            libs_dir=self.base_dir / "libs",
            config_dir=self.base_dir / "config",
            logs_dir=self.base_dir / "logs",
        )

    def prepare(self) -> RuntimePaths:
        """Create required folders and prepend portable dependency folders to sys.path."""
        for folder in (self.paths.libs_dir, self.paths.config_dir, self.paths.logs_dir):
            ensure_directory(folder)

        portable_paths = unique_existing_paths([self.paths.libs_dir, self.paths.embedded_python_dir])
        for path in reversed(portable_paths):
            value = str(path)
            if value not in sys.path:
                sys.path.insert(0, value)

        os.environ.setdefault("PYTHONHOME", str(self.paths.embedded_python_dir))
        os.environ["ENGINE_HOME"] = str(self.paths.base_dir)
        return self.paths

    def python_executable(self) -> Path:
        """Return the expected embedded python.exe path."""
        return self.paths.embedded_python_dir / "python.exe"

    def is_embedded_runtime_available(self) -> bool:
        """Return True when the Windows embeddable runtime has been copied in."""
        return self.python_executable().exists()
