# VoltPy embedded Python runtime

Place the Windows Python 3.12 embeddable distribution here before production use:

- `python.exe`
- `python312.dll`
- Python standard library files/zip
- vendored `site-packages`

VoltPy sets `PYTHONHOME`, `PYTHONPATH` and `PYTHONNOUSERSITE=1` before launching this executable, so apps do not depend on a globally installed Python.
