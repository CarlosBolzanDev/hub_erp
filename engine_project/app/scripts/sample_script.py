from __future__ import annotations

engine_api = None


def register(api) -> None:
    global engine_api
    engine_api = api


def initialize() -> None:
    if engine_api:
        engine_api.log("sample_script initialized", "INFO")
        engine_api.emit_event("sample_script_initialized", {"script": "sample_script"})


def shutdown() -> None:
    if engine_api:
        engine_api.log("sample_script shutdown", "INFO")
