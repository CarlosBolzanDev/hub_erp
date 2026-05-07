# VoltPy portable architecture

VoltPy is a self-contained engine folder designed to be copied into an app. The app owns files such as `App.py`, `main.py`, `teste.py`, and optional `manifest.json`; the engine owns only the `VoltPy/` folder.

## Separation of responsibilities

- **User app directory**: parent directory of `VoltPy/`; contains app entrypoints and app assets.
- **Engine directory**: `VoltPy/`; contains launchers, config, logs, temp files, managed package metadata, optional C# host sources, and embedded runtime assets.
- **Public namespace**: `VoltPy/voltpy`; provides `import voltpy.*` wrappers and the bootstrap/import hook.
- **Vendored Python runtime**: `VoltPy/runtime`; contains the embeddable CPython distribution and `site-packages`.
- **Package registry**: `VoltPy/packages`; contains VoltPy package metadata only and is not placed on `sys.path` to avoid shadowing real libraries.

## Path discovery

The default path model is copy-and-run:

1. locate the engine directory from `VOLTPY_ENGINE_DIR`, `--engine-dir`, or a `VoltPy/` folder in/above the current directory;
2. use the engine parent as the app directory;
3. use `VoltPy/voltpy` as the namespace directory;
4. use `VoltPy/runtime`, `VoltPy/packages`, `VoltPy/logs`, and `VoltPy/temp` for internal runtime state.

Configuration in `VoltPy/config/runtime.json` is optional and can override those defaults. Relative paths are resolved from the copied `VoltPy/` engine directory.

## Entrypoint loading

`ManifestLoader` accepts an optional manifest but does not require one. Entrypoint priority is:

1. explicit CLI/runtime entry;
2. `manifest.json` entry;
3. `App.py`;
4. `main.py`;
5. `teste.py`.

The loader validates that the resolved entry remains inside the app directory.

## Import policy

`VoltPy/voltpy/importing/hook.py` registers `sys.meta_path` finders that:

- resolve `voltpy` and `voltpy.*` from the copied engine namespace directory;
- block direct imports of managed packages (`pandas`, `flask`, `requests`, `sqlalchemy`);
- allow VoltPy wrappers to import real implementations from `runtime/site-packages`.

## Runtime environment

The Python bootstrap and optional C# host set:

- `VOLTPY_ENGINE_DIR=<App>/VoltPy`
- `VOLTPY_APP_DIR=<App>`
- `VOLTPY_NAMESPACE=<App>/VoltPy/voltpy`
- `VOLTPY_RUNTIME=<App>/VoltPy/runtime`
- `VOLTPY_PACKAGES=<App>/VoltPy/packages`
- `VOLTPY_LOGS=<App>/VoltPy/logs`
- `VOLTPY_TEMP=<App>/VoltPy/temp`
- `PYTHONPATH=<App>/VoltPy;<App>/VoltPy/runtime/site-packages;<App>/VoltPy/runtime/Lib`

No top-level `Apps/` folder or repository-specific layout is required.
