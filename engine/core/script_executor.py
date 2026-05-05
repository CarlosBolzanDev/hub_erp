from __future__ import annotations

import importlib.util
import inspect
import logging
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from core.config_manager import EngineManifest, RegisteredScript
from core.runtime_bridge import RuntimePaths
from utils.file_utils import resolve_registered_path
from utils.validation import find_entrypoint, validate_script_file


@dataclass
class ScriptExecutionResult:
    script_id: str
    display_name: str
    path: str
    status: str
    message: str
    return_value: Any = None
    traceback: str | None = None


class ScriptExecutor:
    """Load external scripts by saved path and execute run/main on demand."""

    def __init__(self, runtime_paths: RuntimePaths, logger: logging.Logger) -> None:
        self.runtime_paths = runtime_paths
        self.logger = logger

    def execute_many(
        self,
        scripts: list[RegisteredScript],
        manifest: EngineManifest,
        arguments: str = "",
    ) -> list[ScriptExecutionResult]:
        results: list[ScriptExecutionResult] = []
        stop_on_error = bool(manifest.execution_options.get("stop_on_error", False))
        for script in scripts:
            result = self.execute_one(script, manifest, arguments)
            results.append(result)
            if stop_on_error and result.status == "error":
                self.logger.warning("Execução interrompida após erro em %s.", script.display_name)
                break
        return results

    def execute_one(
        self,
        script: RegisteredScript,
        manifest: EngineManifest,
        arguments: str = "",
    ) -> ScriptExecutionResult:
        script_path = resolve_registered_path(script.path, self.runtime_paths.base_dir)
        script.last_execution = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valid, validation_message = validate_script_file(script_path)
        script.validation_status = validation_message if valid else f"Inválido: {validation_message}"
        if not valid:
            self.logger.error("Script inválido: %s - %s", script.display_name, validation_message)
            return self._result(script, script_path, "error", validation_message)

        self.logger.info("Iniciando execução: %s (%s)", script.display_name, script_path)
        try:
            module = self._load_module(script_path)
            entrypoint = find_entrypoint(module)
            if entrypoint is None:
                message = "Nenhuma função run(context), main(context), run() ou main() foi encontrada."
                self.logger.error("%s: %s", script.display_name, message)
                return self._result(script, script_path, "error", message)

            entrypoint_name, function = entrypoint
            context = self._build_context(script, script_path, manifest, arguments)
            self.logger.info("Chamando %s.%s.", script.display_name, entrypoint_name)
            return_value = self._call_entrypoint(function, context)
            message = self._message_from_return(return_value)
            script.validation_status = "Válido"
            self.logger.info("Execução concluída: %s - %s", script.display_name, message)
            return self._result(script, script_path, "ok", message, return_value=return_value)
        except Exception as exc:
            tb = traceback.format_exc()
            self.logger.error("Erro ao executar %s: %s\n%s", script.display_name, exc, tb)
            return self._result(script, script_path, "error", str(exc), traceback_text=tb)
        finally:
            self._remove_loaded_module(script_path)

    def _load_module(self, script_path: Path) -> ModuleType:
        module_name = f"engine_external_{script_path.stem}_{abs(hash(script_path))}"
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Não foi possível criar spec de importação para {script_path}.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _remove_loaded_module(self, script_path: Path) -> None:
        prefix = f"engine_external_{script_path.stem}_"
        for name in list(sys.modules):
            if name.startswith(prefix):
                sys.modules.pop(name, None)

    def _call_entrypoint(self, function: Any, context: dict[str, Any]) -> Any:
        signature = inspect.signature(function)
        required_parameters = [
            parameter
            for parameter in signature.parameters.values()
            if parameter.default is inspect.Signature.empty
            and parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD, parameter.KEYWORD_ONLY)
        ]
        accepts_varargs = any(
            parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD)
            for parameter in signature.parameters.values()
        )
        if required_parameters or accepts_varargs:
            return function(context)
        return function()

    def _build_context(
        self,
        script: RegisteredScript,
        script_path: Path,
        manifest: EngineManifest,
        arguments: str,
    ) -> dict[str, Any]:
        effective_arguments = arguments if arguments else manifest.default_arguments
        return {
            "paths": {
                "base_dir": str(self.runtime_paths.base_dir),
                "libs_dir": str(self.runtime_paths.libs_dir),
                "config_dir": str(self.runtime_paths.config_dir),
                "logs_dir": str(self.runtime_paths.logs_dir),
                "script_path": str(script_path),
                "script_dir": str(script_path.parent),
            },
            "config": {
                "execution_options": dict(manifest.execution_options),
                "default_arguments": manifest.default_arguments,
            },
            "arguments": effective_arguments,
            "logger": self.logger.getChild(script.display_name.replace(" ", "_")),
            "script_name": script.display_name,
            "script_path": str(script_path),
            "script_id": script.id,
        }

    def _message_from_return(self, return_value: Any) -> str:
        if isinstance(return_value, dict):
            return str(return_value.get("message") or return_value.get("status") or "Executado com sucesso.")
        if return_value is None:
            return "Executado com sucesso."
        return str(return_value)

    def _result(
        self,
        script: RegisteredScript,
        script_path: Path,
        status: str,
        message: str,
        return_value: Any = None,
        traceback_text: str | None = None,
    ) -> ScriptExecutionResult:
        return ScriptExecutionResult(
            script_id=script.id,
            display_name=script.display_name,
            path=str(script_path),
            status=status,
            message=message,
            return_value=return_value,
            traceback=traceback_text,
        )
