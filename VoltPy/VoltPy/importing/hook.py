"""VoltPy import hook based on importlib and sys.meta_path.

The hook creates a virtual public namespace named ``voltpy`` and maps modules such
as ``voltpy.pandas`` to controlled wrapper files stored in the engine namespace.
Direct imports of managed packages are blocked for application code, while wrapper
modules can import the real implementation through ``import_real_module``.
"""

from __future__ import annotations

import contextlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import logging
import os
import sys
import types
from pathlib import Path

LOGGER = logging.getLogger("voltpy.imports")
_NAMESPACE = "voltpy"
_ALLOWED_DIRECT_IMPORTS = {
    "__future__", "abc", "argparse", "builtins", "collections", "contextlib",
    "dataclasses", "datetime", "enum", "functools", "importlib", "inspect", "io",
    "json", "logging", "math", "os", "pathlib", "runpy", "sys", "types", "typing",
}
_MANAGED_PACKAGES = {"pandas", "flask", "requests", "sqlalchemy"}
_INTERNAL_IMPORT_DEPTH = 0
_LOADED_MODULES: list[str] = []
_NAMESPACE_DIR: Path | None = None


class VoltPyImportError(ImportError):
    """Raised when application code violates VoltPy import policy."""


@contextlib.contextmanager
def allow_real_imports():
    """Temporarily allow wrappers to import real Python packages."""
    global _INTERNAL_IMPORT_DEPTH
    _INTERNAL_IMPORT_DEPTH += 1
    try:
        yield
    finally:
        _INTERNAL_IMPORT_DEPTH -= 1


def import_real_module(name: str):
    """Import an underlying Python package from VoltPy-owned wrappers only."""
    with allow_real_imports(), without_namespace_on_path():
        existing = sys.modules.get(name)
        if existing is not None and str(getattr(existing, "__file__", "")).startswith(str(_NAMESPACE_DIR or "")):
            del sys.modules[name]
        LOGGER.info("Importing real module %s for VoltPy wrapper", name)
        return importlib.import_module(name)


@contextlib.contextmanager
def without_namespace_on_path():
    """Hide VoltPy wrapper files while importing real third-party modules."""
    if _NAMESPACE_DIR is None:
        yield
        return

    namespace = str(_NAMESPACE_DIR)
    original = list(sys.path)
    sys.path[:] = [entry for entry in sys.path if str(Path(entry or ".").resolve()) != namespace]
    try:
        yield
    finally:
        sys.path[:] = original


class VoltPyNamespaceFinder(importlib.abc.MetaPathFinder):
    """Resolves ``voltpy`` modules from the engine namespace directory."""

    def __init__(self, namespace_dir: Path):
        self.namespace_dir = namespace_dir

    def find_spec(self, fullname: str, path=None, target=None):  # noqa: D401 - importlib signature
        if fullname == _NAMESPACE:
            init_file = self.namespace_dir / "__init__.py"
            spec = importlib.util.spec_from_file_location(
                fullname,
                init_file,
                submodule_search_locations=[str(self.namespace_dir)],
            )
            return spec

        if not fullname.startswith(f"{_NAMESPACE}."):
            return None

        relative = fullname.removeprefix(f"{_NAMESPACE}.").replace(".", os.sep)
        package_init = self.namespace_dir / relative / "__init__.py"
        module_file = self.namespace_dir / f"{relative}.py"

        if package_init.exists():
            return importlib.util.spec_from_file_location(
                fullname,
                package_init,
                submodule_search_locations=[str(package_init.parent)],
            )
        if module_file.exists():
            return importlib.util.spec_from_file_location(fullname, module_file)
        return None


class VoltPyPolicyFinder(importlib.abc.MetaPathFinder):
    """Blocks direct imports of managed packages from application code."""

    def find_spec(self, fullname: str, path=None, target=None):  # noqa: D401 - importlib signature
        top_level = fullname.partition(".")[0]
        if _INTERNAL_IMPORT_DEPTH > 0 or fullname.startswith(f"{_NAMESPACE}.") or top_level in _ALLOWED_DIRECT_IMPORTS:
            return None

        if top_level in _MANAGED_PACKAGES:
            raise VoltPyImportError(
                f"Direct import '{top_level}' is blocked. Use 'import voltpy.{top_level}' instead."
            )
        return None


class VoltPyAuditLoader(importlib.abc.Loader):
    """Placeholder loader for future virtual modules and audit-only loading."""

    def create_module(self, spec):
        return types.ModuleType(spec.name)

    def exec_module(self, module):
        _LOADED_MODULES.append(module.__name__)
        LOGGER.info("Loaded virtual module %s", module.__name__)


def install(namespace_dir: str | os.PathLike[str] | None = None) -> None:
    """Install VoltPy finders at the beginning of ``sys.meta_path``."""
    global _NAMESPACE_DIR
    resolved = Path(namespace_dir or os.environ.get("VOLTPY_NAMESPACE", Path(__file__).resolve().parents[1])).resolve()
    _NAMESPACE_DIR = resolved

    if not any(isinstance(finder, VoltPyPolicyFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, VoltPyPolicyFinder())
    if not any(isinstance(finder, VoltPyNamespaceFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, VoltPyNamespaceFinder(resolved))

    LOGGER.info("VoltPy import hook installed for namespace dir %s", resolved)


def loaded_modules() -> tuple[str, ...]:
    """Return names observed by VoltPy loaders for diagnostics."""
    return tuple(_LOADED_MODULES)
