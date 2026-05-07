"""VoltPy system diagnostics exposed to apps."""

from __future__ import annotations

import os
from pathlib import Path


def engine_dir() -> Path:
    return Path(os.environ.get("VOLTPY_ENGINE_DIR", Path(__file__).resolve().parents[1])).resolve()


def app_dir() -> Path:
    return Path(os.environ.get("VOLTPY_APP_DIR", engine_dir().parent)).resolve()


def packages_dir() -> Path:
    return Path(os.environ.get("VOLTPY_PACKAGES", engine_dir() / "packages")).resolve()


def logs_dir() -> Path:
    return Path(os.environ.get("VOLTPY_LOGS", engine_dir() / "logs")).resolve()


def app_name() -> str:
    return os.environ.get("VOLTPY_APP_NAME", app_dir().name)
