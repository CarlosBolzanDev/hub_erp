# VoltPy

VoltPy is a modular Windows-oriented engine that hosts isolated Python apps behind a controlled `voltpy` namespace. The host executable and the VoltPy runtime installation are now physically separate: the host reads configuration and points to an external `VoltPyRuntime` root instead of assuming the runtime is beside the executable.

## Target layout

```text
HostApp/
  bin/
  HostApp.exe
  HostApp.dll
  config/
    host.json

VoltPyRuntime/
  VoltPy/
    __init__.py
    bootstrap.py
    pandas.py
    flask.py
    http.py
    database.py
    system.py
    importing/
      hook.py
  Engine/
    VoltPy.Loader/
    VoltPy.Packages/
    VoltPy.Runtime/
    VoltPy.Service/
  Runtime/
    python.exe
    python312.dll
    Lib/
    site-packages/
  Packages/
    pandas/
    requests/
    flask/
    sqlalchemy/
  Apps/
    example_app/
      manifest.json
      main.py
  Logs/
  Temp/
  Config/
    runtime.json
```

In this repository, `VoltPy/` is the sample external runtime root and `HostApp/config/host.json` demonstrates how a host outside that root can point to it.

## Current capabilities

- Starts an internal Python runtime from the configured `RuntimeDirectory` / `PythonExecutable`.
- Resolves `VoltPyRoot`, `NamespaceDirectory`, `RuntimeDirectory`, `PackagesDirectory`, `AppsDirectory`, `LogsDirectory`, and `TempDirectory` from `config/host.json`, environment variables, or command-line arguments.
- Sets `PYTHONHOME`, `PYTHONPATH`, `PYTHONNOUSERSITE=1`, and `VOLTPY_*` variables from the external configuration.
- Runs apps from a `manifest.json` entrypoint under the configured `AppsDirectory`.
- Validates declared package dependencies before execution.
- Installs a Python `sys.meta_path` hook from the configured namespace directory to resolve `voltpy.*` wrappers and block direct imports of managed packages such as `pandas`.
- Logs service, runtime, app, and import activity under the configured `LogsDirectory`.
- Provides an example app using `import voltpy.pandas as pd`.

## Host configuration

The host searches for configuration in this order:

1. `--config <path>`
2. `VOLTPY_HOST_CONFIG`
3. `<host-exe-directory>/config/host.json`
4. `<current-working-directory>/config/host.json`

`VoltPyRoot` can also be overridden with `--voltpy-root <path>` or `VOLTPY_ROOT`. Paths may be absolute or relative. Relative `VoltPyRoot` values are resolved from the configuration file directory; other relative paths are resolved from `VoltPyRoot`.

Example:

```json
{
  "VoltPyRoot": "D:/VoltPyRuntime",
  "NamespaceDirectory": "D:/VoltPyRuntime/VoltPy",
  "RuntimeDirectory": "D:/VoltPyRuntime/Runtime",
  "PackagesDirectory": "D:/VoltPyRuntime/Packages",
  "AppsDirectory": "D:/VoltPyRuntime/Apps",
  "LogsDirectory": "D:/VoltPyRuntime/Logs",
  "TempDirectory": "D:/VoltPyRuntime/Temp",
  "UseSystemPythonFallback": false
}
```

The repository sample keeps child paths relative to `VoltPyRoot`:

```json
{
  "VoltPyRoot": "../../VoltPy",
  "NamespaceDirectory": "VoltPy",
  "RuntimeDirectory": "Runtime",
  "PackagesDirectory": "Packages",
  "AppsDirectory": "Apps",
  "LogsDirectory": "Logs",
  "TempDirectory": "Temp"
}
```

## Preparing the embedded Python runtime on Windows

Copy the Python 3.12 Windows embeddable distribution into the configured `RuntimeDirectory` so the folder contains `python.exe`, `python312.dll`, and the standard library files/zip. Vendor third-party packages into `Runtime/site-packages`. The engine intentionally does not use the Windows global Python installation unless `UseSystemPythonFallback` is true or `--dev-python-fallback` is passed for local development.

## Running

```powershell
dotnet build VoltPy.sln
.\VoltPy\Engine\VoltPy.Service\bin\Debug\net8.0\VoltPy.Service.exe example_app --config .\HostApp\config\host.json
```

Using an explicit external runtime root:

```powershell
.\VoltPy\Engine\VoltPy.Service\bin\Debug\net8.0\VoltPy.Service.exe example_app --voltpy-root "D:\VoltPyRuntime"
```

For a supervised background loop:

```powershell
.\VoltPy\Engine\VoltPy.Service\bin\Debug\net8.0\VoltPy.Service.exe example_app --config .\HostApp\config\host.json --supervise
```

## Application contract

Apps must declare a manifest:

```json
{
  "name": "ExampleApp",
  "version": "1.0",
  "entry": "main.py",
  "dependencies": ["pandas"]
}
```

Apps should import through VoltPy:

```python
import voltpy.pandas as pd
```

Direct imports of managed libraries are intentionally blocked:

```python
import pandas  # blocked; use import voltpy.pandas as pd
```
