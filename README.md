# VoltPy

VoltPy is a modular Windows-oriented engine that hosts isolated Python apps behind a controlled `voltpy` namespace. The first implementation uses a .NET 8 C# core and launches an embedded CPython runtime by subprocess, with all Python paths configured by the engine so applications do not rely on a globally installed Python.

## Layout

```text
VoltPy/
├── Engine/
│   ├── VoltPy.Runtime/
│   ├── VoltPy.Loader/
│   ├── VoltPy.Packages/
│   └── VoltPy.Service/
├── Runtime/
├── Packages/
├── Apps/example_app/
├── VoltPy/
├── Logs/
├── Temp/
└── Config/
```

## Current capabilities

- Starts an internal Python runtime from `VoltPy/Runtime/python.exe`.
- Sets `PYTHONHOME`, `PYTHONPATH`, `PYTHONNOUSERSITE=1`, and VoltPy-specific environment variables.
- Runs apps from a `manifest.json` entrypoint.
- Validates declared package dependencies before execution.
- Installs a Python `sys.meta_path` hook to resolve `voltpy.*` wrappers and block direct imports of managed packages such as `pandas`.
- Logs service, runtime, app, and import activity under `VoltPy/Logs`.
- Provides an example app using `import voltpy.pandas as pd`.

## Preparing the embedded Python runtime on Windows

Copy the Python 3.12 Windows embeddable distribution into `VoltPy/Runtime` so the folder contains `python.exe`, `python312.dll`, and the standard library files/zip. Vendor third-party packages into `VoltPy/Runtime/site-packages` or managed package folders. The engine intentionally does not use the Windows global Python installation unless `--dev-python-fallback` is passed for local development.

## Running

```powershell
dotnet build VoltPy.sln
.\VoltPy\Engine\VoltPy.Service\bin\Debug\net8.0\VoltPy.Service.exe example_app
```

For a supervised background loop:

```powershell
.\VoltPy\Engine\VoltPy.Service\bin\Debug\net8.0\VoltPy.Service.exe example_app --supervise
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

## Technical references used

The architecture follows Python's documented import system, where meta path finders in `sys.meta_path` participate in import resolution before path-based imports, and the embeddable Windows package model described by the Python documentation. The .NET service is implemented as a dependency-light `WinExe` process suitable for a Windows Service wrapper in this first version.
