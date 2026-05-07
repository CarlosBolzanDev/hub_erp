"""VoltPy Python bootstrap executed by the C# runtime host.

The bootstrap is intentionally configured by environment variables so the host
program can live outside the physical VoltPyRuntime installation.
"""

from __future__ import annotations

import logging
import os
import runpy
import sys
from pathlib import Path


def _resolve_directory(env_name: str, fallback: Path) -> Path:
    configured = os.environ.get(env_name)
    return Path(configured).resolve() if configured else fallback.resolve()


NAMESPACE_DIR = _resolve_directory("VOLTPY_NAMESPACE", Path(__file__).resolve().parent)
ROOT_DIR = _resolve_directory("VOLTPY_ROOT", NAMESPACE_DIR.parent)
RUNTIME_DIR = _resolve_directory("VOLTPY_RUNTIME", ROOT_DIR / "Runtime")
PACKAGES_DIR = _resolve_directory("VOLTPY_PACKAGES", ROOT_DIR / "Packages")
LOGS_DIR = _resolve_directory("VOLTPY_LOGS", ROOT_DIR / "Logs")
TEMP_DIR = _resolve_directory("VOLTPY_TEMP", ROOT_DIR / "Temp")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "python-imports.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Ensure configured runtime paths win over user paths. PackagesDirectory is kept
# in VOLTPY_PACKAGES for managed metadata and future package routing; real
# importable libraries are expected in Runtime/site-packages for this version.
for candidate in (NAMESPACE_DIR, RUNTIME_DIR / "site-packages", RUNTIME_DIR / "Lib"):
    candidate_text = str(candidate)
    if candidate.exists() and candidate_text not in sys.path:
        sys.path.insert(0, candidate_text)

from importing.hook import install  # noqa: E402

install(NAMESPACE_DIR)


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: bootstrap.py <app-entry.py>")

    entry = Path(sys.argv[1]).resolve()
    app_dir = entry.parent
    sys.path.insert(0, str(app_dir))
    sys.argv = [str(entry), *sys.argv[2:]]

    logging.getLogger("voltpy.bootstrap").info(
        "Running app entry %s with namespace=%s packages=%s runtime=%s",
        entry,
        NAMESPACE_DIR,
        PACKAGES_DIR,
        RUNTIME_DIR,
    )
    runpy.run_path(str(entry), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
