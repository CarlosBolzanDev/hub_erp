"""Sample plugin script demonstrating the runtime API."""

from __future__ import annotations

_ENGINE = None


def register(engine) -> None:
    global _ENGINE
    _ENGINE = engine


def initialize() -> None:
    if _ENGINE:
        _ENGINE.logger.info("sample_script initialized")


def shutdown() -> None:
    if _ENGINE:
        _ENGINE.logger.info("sample_script shutdown")
