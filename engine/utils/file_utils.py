from __future__ import annotations

from pathlib import Path
from typing import Iterable


def ensure_directory(path: Path) -> Path:
    """Create *path* when it does not exist and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_path(path: Path) -> Path:
    """Return an absolute, resolved path without requiring the path to exist."""
    return path.expanduser().resolve(strict=False)


def is_relative_to(child: Path, parent: Path) -> bool:
    """Compatibility wrapper for Path.is_relative_to."""
    try:
        child.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def sorted_python_files(folder: Path) -> list[Path]:
    """Return direct child Python files sorted by case-insensitive name."""
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted(
        (item for item in folder.iterdir() if item.is_file() and item.suffix.lower() == ".py"),
        key=lambda item: item.name.casefold(),
    )


def unique_existing_paths(paths: Iterable[Path]) -> list[Path]:
    """Return unique existing paths while preserving input order."""
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        normalized = normalize_path(path)
        if normalized.exists() and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result
