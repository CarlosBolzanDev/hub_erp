from __future__ import annotations

import json
import shlex
import traceback
from pathlib import Path
from typing import Any

from config_manager import ConfigManager
from logger import ScriptLogger
from script_loader import ScriptContractError, ScriptLoader


class RuntimeBridge:
    """Coordinates context creation, script execution, exception capture and output."""

    def __init__(self, script_path: str | Path, context_file: str | Path, log_file: str | Path) -> None:
        self.script_path = Path(script_path).resolve()
        self.context_file = Path(context_file).resolve()
        self.log_file = Path(log_file).resolve()
        self.logger = ScriptLogger(self.log_file)
        self.loader = ScriptLoader()

    def run(self) -> dict[str, Any]:
        try:
            context = self._build_context()
            self.logger.info(f"Iniciando script: {self.script_path}")
            result = self.loader.execute(self.script_path, context)
            self.logger.info("Script finalizado com sucesso.")
            return {
                "status": "ok",
                "message": "Script executado com sucesso.",
                "result": self._json_safe(result),
            }
        except ScriptContractError as exc:
            self.logger.error(str(exc))
            return {"status": "error", "message": str(exc), "type": "contract_error"}
        except Exception as exc:
            trace = traceback.format_exc()
            self.logger.exception(f"Erro durante a execução: {exc}")
            return {
                "status": "error",
                "message": f"Erro durante a execução do script: {exc}",
                "type": exc.__class__.__name__,
                "traceback": trace,
            }

    def _build_context(self) -> dict[str, Any]:
        with self.context_file.open("r", encoding="utf-8") as file:
            context = json.load(file)

        args_text = context.get("args") or ""
        context["args_list"] = shlex.split(args_text, posix=False) if args_text else []
        context["logger"] = self.logger
        context["config_manager"] = ConfigManager(context.get("config_dir", self.context_file.parent))
        context["engine"] = {
            "script_path": str(self.script_path),
            "log_file": str(self.log_file),
        }
        return context

    def _json_safe(self, value: Any) -> Any:
        try:
            json.dumps(value, ensure_ascii=False)
            return value
        except TypeError:
            return repr(value)
