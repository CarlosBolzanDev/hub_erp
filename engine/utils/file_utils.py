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


def resolve_registered_path(path_value: str, base_dir: Path) -> Path:
    """Resolve an absolute or engine-relative script path from the manifest."""
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve(strict=False)


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
