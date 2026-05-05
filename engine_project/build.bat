@echo off
setlocal
pyinstaller --noconfirm build.spec
echo Build finalizado em dist\GenericRuntime
endlocal
