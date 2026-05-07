# VoltPy

VoltPy is now a portable, copy-and-run Python engine. To use it in another app, copy the `VoltPy/` folder into the app directory and run the app through the VoltPy launcher. The engine resolves paths relative to where the copied `VoltPy/` folder lives, not relative to this repository.

## What was wrong before

The previous layout looked like a repository-hosted runtime: it assumed `Apps/`, external host configuration, a separate runtime root, and repository-specific conventions. That made reuse harder because a consuming app needed to reproduce the original repo layout or pass several path options.

The refactor removes that coupling. `VoltPy/` is the distributable engine folder; the user app is simply the parent directory that contains it.

## Final portable tree

A consuming app can be as small as:

```text
MyApp/
  App.py          # first priority entrypoint
  main.py         # second priority entrypoint
  teste.py        # third priority entrypoint
  manifest.json   # optional
  VoltPy/         # copied engine folder
    run.py
    __init__.py
    voltpy/
      __init__.py
      bootstrap.py
      pandas.py
      flask.py
      http.py
      database.py
      system.py
      importing/
        hook.py
    runtime/
      python.exe
      python312.dll
      Lib/
      site-packages/
    packages/
      pandas/
      flask/
      requests/
      sqlalchemy/
    logs/
    temp/
    config/
      runtime.json
```

The C# projects under `VoltPy/Engine/` are optional host/service sources for applications that want a compiled Windows host. They now resolve the app root as the parent of the copied `VoltPy/` engine folder and no longer require a top-level `Apps/` directory.

## Entrypoint discovery

Manifest files are optional. VoltPy runs the first existing file in this order:

1. explicit entry argument, for example `python VoltPy/run.py custom.py`
2. `manifest.json` with `{ "entry": "..." }`
3. `App.py`
4. `main.py`
5. `teste.py`

## Running with Python directly

From inside the app directory:

```powershell
python .\VoltPy\run.py
```

Or with an explicit entrypoint:

```powershell
python .\VoltPy\run.py .\teste.py
```

## Running with the optional C# host

```powershell
dotnet build VoltPy.sln
.\VoltPy\Engine\VoltPy.Service\bin\Debug\net8.0\VoltPy.Service.exe --engine-dir .\VoltPy
```

## Runtime isolation

VoltPy sets the runtime paths from the copied engine folder:

- engine: `MyApp/VoltPy`
- namespace: `MyApp/VoltPy/voltpy`
- embedded Python: `MyApp/VoltPy/runtime`
- vendored libraries: `MyApp/VoltPy/runtime/site-packages`
- package metadata: `MyApp/VoltPy/packages`
- logs: `MyApp/VoltPy/logs`
- temp: `MyApp/VoltPy/temp`

The engine still supports controlled imports:

```python
import voltpy.pandas as pd
from voltpy.database import Database
```

Direct imports of managed packages such as `import pandas` are blocked by the import hook so applications depend on VoltPy facades instead of third-party implementations.

## Optional manifest

If present, `manifest.json` can remain very small:

```json
{
  "name": "MyApp",
  "entry": "App.py",
  "dependencies": ["pandas"]
}
```

If absent, VoltPy discovers `App.py`, `main.py`, or `teste.py` automatically.

## Preparing embedded Python on Windows

For production, place the Python 3.12 Windows embeddable distribution in `VoltPy/runtime` so it contains `python.exe`, `python312.dll`, the standard library, and vendored dependencies under `VoltPy/runtime/site-packages`. The optional C# host can use `--dev-python-fallback` only for local development.
