@echo off
setlocal
set "ENGINE_DIR=%~dp0"
"%ENGINE_DIR%python\python.exe" "%ENGINE_DIR%engine_gui.py"
endlocal
