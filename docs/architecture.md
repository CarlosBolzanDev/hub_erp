# VoltPy architecture

VoltPy is split into a host process and an external runtime installation. The host can live under `HostApp/` (or any product directory), while `VoltPyRuntime/` owns the Python namespace, embedded CPython files, managed package registry, apps, logs, temp files, and runtime config.

## Modules

- `VoltPy.Runtime`: external path configuration, log writing, Python environment construction, and subprocess execution.
- `VoltPy.Loader`: app manifest parsing, dependency validation orchestration, and app entry execution from the configured `AppsDirectory`.
- `VoltPy.Packages`: internal package registry and dependency checks, prepared for future `voltpy install` commands.
- `VoltPy.Service`: invisible `WinExe` host that can run once or supervise/restart an app and accepts `--config` / `--voltpy-root`.
- `VoltPyRuntime/VoltPy`: Python namespace facade and import hook runtime.

## Configuration and path resolution

The host loads `VoltPyPathOptions` from `config/host.json`, `VOLTPY_HOST_CONFIG`, CLI arguments, or environment variables. `VoltPyRoot` can be absolute or relative to the config file directory. Child paths such as `NamespaceDirectory`, `RuntimeDirectory`, `PackagesDirectory`, `AppsDirectory`, `LogsDirectory`, and `TempDirectory` can also be absolute or relative to `VoltPyRoot`.

This means no critical runtime code depends on the host executable being inside the same directory as `VoltPyRuntime`.

## Import policy

`VoltPyRuntime/VoltPy/importing/hook.py` registers two `sys.meta_path` finders:

1. `VoltPyNamespaceFinder` maps `voltpy` and `voltpy.*` imports to wrapper modules in the configured namespace directory.
2. `VoltPyPolicyFinder` blocks direct imports of managed packages from app code.

Wrappers call `import_real_module()` to temporarily allow imports of the real implementation. This keeps app code coupled to VoltPy APIs rather than third-party packages and enables future changes such as sandboxing, package version routing, or implementation swaps.

## Runtime isolation

The C# host constructs an explicit environment from the external configuration:

- `PYTHONHOME=<RuntimeDirectory or PythonHome>`
- `PYTHONPATH=<NamespaceDirectory>;<RuntimeDirectory>/site-packages;<RuntimeDirectory>/Lib;<AdditionalPythonPath>`
- `PYTHONNOUSERSITE=1`
- `VOLTPY_ROOT=<VoltPyRoot>`
- `VOLTPY_NAMESPACE=<NamespaceDirectory>`
- `VOLTPY_PACKAGES=<PackagesDirectory>`
- `VOLTPY_RUNTIME=<RuntimeDirectory>`
- `VOLTPY_APPS=<AppsDirectory>`
- `VOLTPY_LOGS=<LogsDirectory>`
- `VOLTPY_TEMP=<TempDirectory>`

The Python bootstrap uses those variables first and only falls back to its own file location when run manually for diagnostics.

## Future expansion points

- Replace subprocess hosting with Python.NET or native CPython embedding.
- Add signed package manifests and multiple package versions.
- Add a sandbox policy layer for filesystem, network, and import permissions.
- Add CLI commands such as `voltpy install pandas` and `voltpy run app`.
- Add RPC between .NET services and Python apps.
