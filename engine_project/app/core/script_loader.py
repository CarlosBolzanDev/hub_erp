from __future__ import annotations

from dataclasses import dataclass, field
import importlib.util
from pathlib import Path
import traceback
from types import ModuleType
from typing import Any


@dataclass
class ScriptRecord:
    name: str
    path: Path
    module: ModuleType | None = None
    active: bool = False
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ScriptLoader:
    def __init__(self, logger: Any) -> None:
        self._logger = logger
        self._scripts: dict[str, ScriptRecord] = {}

    @property
    def scripts(self) -> dict[str, ScriptRecord]:
        return self._scripts

    def load_path(self, file_path: Path, engine_api: Any, auto_activate: bool = False) -> None:
        name = file_path.stem
        record = ScriptRecord(name=name, path=file_path)
        self._scripts[name] = record
        try:
            spec = importlib.util.spec_from_file_location(f"runtime_script_{name}", file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to build import spec for {name}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._validate_script_interface(module, name)
            module.register(engine_api)
            record.module = module
            self._logger.info("Script '%s' loaded from %s.", name, file_path)
            if auto_activate:
                self.activate(name)
        except Exception as exc:
            record.last_error = f"{exc}\n{traceback.format_exc()}"
            self._logger.error("Failed to load script '%s': %s", file_path, exc)

    def _validate_script_interface(self, module: ModuleType, name: str) -> None:
        for fn in ("register", "initialize", "shutdown"):
            if not hasattr(module, fn):
                raise AttributeError(f"Script '{name}' is missing required function: {fn}")

    def unload(self, name: str) -> None:
        record = self._scripts.get(name)
        if not record:
            return
        if record.module and record.active:
            try:
                record.module.shutdown()
            except Exception as exc:
                self._logger.error("Error while shutting down '%s': %s", name, exc)
        self._scripts.pop(name, None)
        self._logger.info("Script '%s' removed.", name)

    def deactivate(self, name: str) -> None:
        record = self._scripts.get(name)
        if not record or not record.module or not record.active:
            self._logger.info("Script '%s' is already inactive.", name)
            return
        try:
            record.module.shutdown()
            record.active = False
            self._logger.info("Script '%s' deactivated.", name)
        except Exception as exc:
            record.last_error = f"{exc}\n{traceback.format_exc()}"
            self._logger.error("Error while deactivating '%s': %s", name, exc)

    def activate(self, name: str, force_restart: bool = False) -> None:
        record = self._scripts.get(name)
        if not record or not record.module:
            self._logger.error("Script '%s' is not loaded.", name)
            return
        if record.active and not force_restart:
            self._logger.info("Script '%s' is already active.", name)
            return
        try:
            if record.active and force_restart:
                record.module.shutdown()
                record.active = False
            record.module.initialize()
            record.active = True
            self._logger.info("Script '%s' activated.", name)
        except Exception as exc:
            record.last_error = f"{exc}\n{traceback.format_exc()}"
            record.active = False
            self._logger.error("Error while activating '%s': %s", name, exc)

    def reload(self, name: str, engine_api: Any) -> None:
        record = self._scripts.get(name)
        if not record:
            self._logger.error("Script '%s' not found for reload.", name)
            return
        path = record.path
        was_active = record.active
        self.unload(name)
        self.load_path(path, engine_api, auto_activate=was_active)

    def shutdown_all(self) -> None:
        for name in list(self._scripts.keys()):
            self.deactivate(name)
