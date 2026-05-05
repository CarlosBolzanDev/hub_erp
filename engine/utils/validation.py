from __future__ import annotations

import ast
import re
from pathlib import Path

_SCRIPT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+\.py$")
_IGNORED_PREFIXES = ("_", ".")


class ScriptValidationError(ValueError):
    """Raised when an external script cannot be accepted by the engine."""


def is_candidate_script(path: Path) -> bool:
    """Return True when *path* looks like a user-runnable Python script."""
    name = path.name
    if not path.is_file() or path.suffix.lower() != ".py":
        return False
    if name.startswith(_IGNORED_PREFIXES):
        return False
    if name in {"__init__.py", "__main__.py"}:
        return False
    return bool(_SCRIPT_NAME_PATTERN.match(name))


def validate_script_file(path: Path) -> tuple[bool, str]:
    """Validate basic script shape without executing the script."""
    if not is_candidate_script(path):
        return False, "Arquivo ignorado: nome, extensão ou tipo inválido."
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "Arquivo ignorado: não está codificado em UTF-8."
    except OSError as exc:
        return False, f"Arquivo ignorado: erro de leitura ({exc})."

    try:
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return False, f"Arquivo ignorado: erro de sintaxe na linha {exc.lineno}."

    return True, "Script válido."


def find_entrypoint(module: object):
    """Return run(context) or main(context) from a loaded module, or None."""
    for name in ("run", "main"):
        candidate = getattr(module, name, None)
        if callable(candidate):
            return name, candidate
    return None
