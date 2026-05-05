from __future__ import annotations

import importlib.util
import logging
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from core.config_manager import EngineSettings
from core.runtime_bridge import RuntimePaths
from utils.file_utils import is_relative_to
from utils.validation import find_entrypoint, validate_script_file


@dataclass
class ScriptExecutionResult:
    script: str
    status: str
    message: str
    return_value: Any = None
    traceback: str | None = None


class ScriptExecutor:
    """Load external scripts on demand and execute run(context) or main(context)."""

    def __init__(self, runtime_paths: RuntimePaths, logger: logging.Logger) -> None:
        self.runtime_paths = runtime_paths
        self.logger = logger

    def execute_many(
        self,
        script_names: list[str],
        settings: EngineSettings,
        arguments: str = "",
    ) -> list[ScriptExecutionResult]:
        results: list[ScriptExecutionResult] = []
        stop_on_error = bool(settings.execution_options.get("stop_on_error", False))
        for script_name in script_names:
            result = self.execute_one(script_name, settings, arguments)
            results.append(result)
            if stop_on_error and result.status == "error":
                self.logger.warning("Execução interrompida após erro em %s.", script_name)
                break
        return results

    def execute_one(
        self,
        script_name: str,
        settings: EngineSettings,
        arguments: str = "",
    ) -> ScriptExecutionResult:
        script_path = (self.runtime_paths.scripts_dir / script_name).resolve(strict=False)
        if not is_relative_to(script_path, self.runtime_paths.scripts_dir):
            return ScriptExecutionResult(script_name, "error", "Caminho do script fora da pasta Scripts.")

        valid, validation_message = validate_script_file(script_path)
        if not valid:
            self.logger.error("Script inválido: %s - %s", script_name, validation_message)
            return ScriptExecutionResult(script_name, "error", validation_message)

        self.logger.info("Iniciando execução: %s", script_name)
        try:
            module = self._load_module(script_path)
            entrypoint = find_entrypoint(module)
            if entrypoint is None:
                message = "Nenhuma função run(context) ou main(context) foi encontrada."
                self.logger.error("%s: %s", script_name, message)
                return ScriptExecutionResult(script_name, "error", message)

            entrypoint_name, function = entrypoint
            context = self._build_context(script_path, settings, arguments)
            self.logger.info("Chamando %s.%s(context).", script_name, entrypoint_name)
            return_value = function(context)
            message = self._message_from_return(return_value)
            self.logger.info("Execução concluída: %s - %s", script_name, message)
            return ScriptExecutionResult(script_name, "ok", message, return_value=return_value)
        except Exception as exc:
            tb = traceback.format_exc()
            self.logger.error("Erro ao executar %s: %s\n%s", script_name, exc, tb)
            return ScriptExecutionResult(script_name, "error", str(exc), traceback=tb)
        finally:
            self._remove_loaded_module(script_path)

    def _load_module(self, script_path: Path) -> ModuleType:
        module_name = f"engine_external_{script_path.stem}_{abs(hash(script_path))}"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Não foi possível criar spec de importação para {script_path.name}.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _remove_loaded_module(self, script_path: Path) -> None:
        prefix = f"engine_external_{script_path.stem}_"
        for name in list(sys.modules):
            if name.startswith(prefix):
                sys.modules.pop(name, None)

    def _build_context(self, script_path: Path, settings: EngineSettings, arguments: str) -> dict[str, Any]:
        effective_arguments = arguments if arguments else settings.default_arguments
        return {
            "paths": {
                "base_dir": str(self.runtime_paths.base_dir),
                "scripts_dir": str(self.runtime_paths.scripts_dir),
                "libs_dir": str(self.runtime_paths.libs_dir),
                "config_dir": str(self.runtime_paths.config_dir),
                "logs_dir": str(self.runtime_paths.logs_dir),
                "script_path": str(script_path),
            },
            "settings": {
                "selected_scripts": list(settings.selected_scripts),
                "execution_options": dict(settings.execution_options),
                "default_arguments": settings.default_arguments,
            },
            "arguments": effective_arguments,
            "logger": self.logger.getChild(script_path.stem),
        }

    def _message_from_return(self, return_value: Any) -> str:
        if isinstance(return_value, dict):
            return str(return_value.get("message") or return_value.get("status") or "Executado com sucesso.")
        if return_value is None:
            return "Executado com sucesso."
        return str(return_value)
