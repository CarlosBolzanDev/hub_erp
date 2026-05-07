"""Portable VoltPy bootstrap.

Copy the ``VoltPy`` engine folder into any application directory and run this
bootstrap to execute the nearest app entrypoint. The app root is discovered from
``VOLTPY_APP_DIR`` or from the parent directory of the engine folder.
"""

from __future__ import annotations

import json
import logging
import os
import runpy
import sys
from pathlib import Path

ENTRYPOINT_PRIORITY = ("App.py", "main.py", "teste.py")


def _resolve_directory(env_name: str, fallback: Path) -> Path:
    configured = os.environ.get(env_name)
    return Path(configured).resolve() if configured else fallback.resolve()


PACKAGE_DIR = Path(__file__).resolve().parent
ENGINE_DIR = _resolve_directory("VOLTPY_ENGINE_DIR", PACKAGE_DIR.parent)
APP_DIR = _resolve_directory("VOLTPY_APP_DIR", ENGINE_DIR.parent)
RUNTIME_DIR = _resolve_directory("VOLTPY_RUNTIME", ENGINE_DIR / "runtime")
PACKAGES_DIR = _resolve_directory("VOLTPY_PACKAGES", ENGINE_DIR / "packages")
LOGS_DIR = _resolve_directory("VOLTPY_LOGS", ENGINE_DIR / "logs")
TEMP_DIR = _resolve_directory("VOLTPY_TEMP", ENGINE_DIR / "temp")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "voltpy.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Keep the embedded engine and vendored packages ahead of user/global paths.
for candidate in (ENGINE_DIR, RUNTIME_DIR / "site-packages", RUNTIME_DIR / "Lib"):
    candidate_text = str(candidate)
    if candidate.exists() and candidate_text not in sys.path:
        sys.path.insert(0, candidate_text)

from voltpy.importing.hook import install  # noqa: E402

install(PACKAGE_DIR)


def _manifest_entry(app_dir: Path) -> str | None:
    manifest_path = app_dir / "manifest.json"
    if not manifest_path.exists():
        return None

    with manifest_path.open("r", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)
    entry = manifest.get("entry")
    return str(entry) if entry else None


def discover_entrypoint(app_dir: Path, explicit_entry: str | None = None) -> Path:
    """Find the app entrypoint using explicit arg, manifest, then defaults."""
    candidates = [explicit_entry, _manifest_entry(app_dir), *ENTRYPOINT_PRIORITY]
    for candidate in candidates:
        if not candidate:
            continue
        entry = (app_dir / candidate).resolve()
        try:
            entry.relative_to(app_dir)
        except ValueError as exc:
            raise RuntimeError(f"VoltPy entrypoint escapes app directory: {entry}") from exc
        if entry.is_file():
            return entry

    priorities = ", ".join(ENTRYPOINT_PRIORITY)
    raise FileNotFoundError(f"No VoltPy entrypoint found in {app_dir}. Expected one of: {priorities}.")


def main() -> int:
    explicit_entry = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VOLTPY_ENTRY")
    entry = discover_entrypoint(APP_DIR, explicit_entry)

    os.environ.setdefault("VOLTPY_ENGINE_DIR", str(ENGINE_DIR))
    os.environ.setdefault("VOLTPY_APP_DIR", str(APP_DIR))
    os.environ.setdefault("VOLTPY_PACKAGES", str(PACKAGES_DIR))
    os.environ.setdefault("VOLTPY_LOGS", str(LOGS_DIR))
    os.environ.setdefault("VOLTPY_TEMP", str(TEMP_DIR))
    os.environ.setdefault("VOLTPY_APP_NAME", APP_DIR.name)

    app_dir_text = str(APP_DIR)
    if app_dir_text not in sys.path:
        sys.path.insert(0, app_dir_text)
    sys.argv = [str(entry), *sys.argv[2:]]

    logging.getLogger("voltpy.bootstrap").info(
        "Running entry=%s app_dir=%s engine_dir=%s packages=%s runtime=%s",
        entry,
        APP_DIR,
        ENGINE_DIR,
        PACKAGES_DIR,
        RUNTIME_DIR,
    )
    runpy.run_path(str(entry), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
