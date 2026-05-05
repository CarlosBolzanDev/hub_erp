$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$project = Join-Path $root "src\WindowsPythonLauncher\WindowsPythonLauncher.csproj"
$publish = Join-Path $root "dist\project"

New-Item -ItemType Directory -Force -Path $publish | Out-Null
dotnet publish $project -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o $publish

Copy-Item -Path (Join-Path $root "engine") -Destination $publish -Recurse -Force
Copy-Item -Path (Join-Path $root "Scripts") -Destination $publish -Recurse -Force
Copy-Item -Path (Join-Path $root "config") -Destination $publish -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $publish "logs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $publish "assets") | Out-Null

Write-Host "Package ready: $publish"
Write-Host "Entry point: $(Join-Path $publish 'main.exe')"
