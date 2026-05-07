# VoltPy architecture

## Modules

- `VoltPy.Runtime`: path discovery, log writing, Python environment construction, and subprocess execution.
- `VoltPy.Loader`: app manifest parsing, dependency validation orchestration, and app entry execution.
- `VoltPy.Packages`: internal package registry and dependency checks, prepared for future `voltpy install` commands.
- `VoltPy.Service`: invisible `WinExe` host that can run once or supervise/restart an app.
- `VoltPy/VoltPy`: Python namespace facade and import hook runtime.

## Import policy

`VoltPy/VoltPy/importing/hook.py` registers two `sys.meta_path` finders:

1. `VoltPyNamespaceFinder` maps `voltpy` and `voltpy.*` imports to engine-owned wrapper modules.
2. `VoltPyPolicyFinder` blocks direct imports of managed packages from app code.

Wrappers call `import_real_module()` to temporarily allow imports of the real implementation. This keeps app code coupled to VoltPy APIs rather than third-party packages and enables future changes such as sandboxing, package version routing, or implementation swaps.

## Runtime isolation

The C# host constructs an explicit environment:

- `PYTHONHOME=VoltPy/Runtime`
- `PYTHONPATH=VoltPy/VoltPy;VoltPy/Runtime/site-packages;VoltPy/Runtime/Lib`
- `PYTHONNOUSERSITE=1`
- `VOLTPY_*` variables for app and engine directories

This prevents dependency on Python installed on the user's Windows machine.

## Future expansion points

- Replace subprocess hosting with Python.NET or native CPython embedding.
- Add signed package manifests and multiple package versions.
- Add a sandbox policy layer for filesystem, network, and import permissions.
- Add CLI commands such as `voltpy install pandas` and `voltpy run app`.
- Add RPC between .NET services and Python apps.
