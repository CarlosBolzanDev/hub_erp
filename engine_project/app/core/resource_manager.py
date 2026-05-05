from __future__ import annotations

from pathlib import Path
import sys


class ResourceManager:
    """Resolves paths in source and PyInstaller runtime modes."""

    def __init__(self) -> None:
        self._base_path = self._detect_base_path()

    @staticmethod
    def _detect_base_path() -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)  # type: ignore[attr-defined]
        return Path(__file__).resolve().parents[2]

    @property
    def base_path(self) -> Path:
        return self._base_path

    def resolve(self, *parts: str) -> Path:
        return self._base_path.joinpath(*parts)

    def runtime_writable_path(self, *parts: str) -> Path:
        root = Path.cwd() / "runtime_data"
        root.mkdir(parents=True, exist_ok=True)
        path = root.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
