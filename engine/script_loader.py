from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class ScriptContractError(RuntimeError):
    """Raised when a script does not implement the expected run/main contract."""


class ScriptLoader:
    """Load a .py file as a fresh module and execute its run(context) or main(context)."""

    def load(self, script_path: str | Path) -> ModuleType:
        path = Path(script_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Script não encontrado: {path}")
        if path.suffix.lower() != ".py":
            raise ScriptContractError(f"Arquivo não é um script Python .py: {path.name}")

        module_name = f"external_script_{path.stem}_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ScriptContractError(f"Não foi possível carregar o módulo: {path.name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(module_name, None)
        return module

    def get_entrypoint(self, module: ModuleType) -> Callable[[dict[str, Any]], Any]:
        entrypoint = getattr(module, "run", None) or getattr(module, "main", None)
        if entrypoint is None or not callable(entrypoint):
            raise ScriptContractError("O script deve exportar uma função run(context) ou main(context).")
        return entrypoint

    def execute(self, script_path: str | Path, context: dict[str, Any]) -> Any:
        module = self.load(script_path)
        entrypoint = self.get_entrypoint(module)
        return entrypoint(context)
