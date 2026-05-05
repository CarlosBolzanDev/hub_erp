from __future__ import annotations

import ast
from pathlib import Path


class ScriptValidationError(ValueError):
    """Raised when an external script cannot be accepted by the engine."""


def validate_script_file(path: Path) -> tuple[bool, str]:
    """Validate an external script path without executing the script."""
    if not path.exists():
        return False, "Arquivo não encontrado."
    if not path.is_file():
        return False, "O caminho não aponta para um arquivo."
    if path.suffix.lower() != ".py":
        return False, "O arquivo não possui extensão .py."

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "Arquivo não está codificado em UTF-8."
    except OSError as exc:
        return False, f"Erro de leitura ({exc})."

    try:
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return False, f"Erro de sintaxe na linha {exc.lineno}."

    return True, "Válido"


def find_entrypoint(module: object):
    """Return run or main from a loaded module, or None."""
    for name in ("run", "main"):
        candidate = getattr(module, name, None)
        if callable(candidate):
            return name, candidate
    return None
