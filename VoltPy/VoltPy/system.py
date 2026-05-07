"""VoltPy system diagnostics exposed to apps."""

from __future__ import annotations

import os
from pathlib import Path


def root() -> Path:
    return Path(os.environ["VOLTPY_ROOT"]).resolve()


def app_dir() -> Path:
    return Path(os.environ["VOLTPY_APP_DIR"]).resolve()


def app_name() -> str:
    return os.environ.get("VOLTPY_APP_NAME", "unknown")
