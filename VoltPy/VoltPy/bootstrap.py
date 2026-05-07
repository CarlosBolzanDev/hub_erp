"""VoltPy Python bootstrap executed by the C# runtime host."""

from __future__ import annotations

import logging
import os
import runpy
import sys
from pathlib import Path

NAMESPACE_DIR = Path(os.environ.get("VOLTPY_NAMESPACE", Path(__file__).resolve().parent)).resolve()
LOGS_DIR = Path(os.environ.get("VOLTPY_LOGS", NAMESPACE_DIR.parent / "Logs")).resolve()
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "python-imports.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Ensure the engine namespace wins over user paths.
sys.path.insert(0, str(NAMESPACE_DIR))
sys.path.insert(0, str(NAMESPACE_DIR.parent / "Runtime" / "site-packages"))

from importing.hook import install  # noqa: E402

install(NAMESPACE_DIR)


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: bootstrap.py <app-entry.py>")

    entry = Path(sys.argv[1]).resolve()
    app_dir = entry.parent
    sys.path.insert(0, str(app_dir))
    sys.argv = [str(entry), *sys.argv[2:]]

    logging.getLogger("voltpy.bootstrap").info("Running app entry %s", entry)
    runpy.run_path(str(entry), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
