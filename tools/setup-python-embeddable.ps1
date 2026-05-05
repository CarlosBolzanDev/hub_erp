param(
    [string]$Version = "3.12.4",
    [string]$Architecture = "amd64"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$pythonDir = Join-Path $root "engine\python"
$tempDir = Join-Path $root ".tmp"
$zipName = "python-$Version-embed-$Architecture.zip"
$url = "https://www.python.org/ftp/python/$Version/$zipName"
$zipPath = Join-Path $tempDir $zipName

New-Item -ItemType Directory -Force -Path $pythonDir, $tempDir | Out-Null
Write-Host "Downloading $url"
Invoke-WebRequest -Uri $url -OutFile $zipPath
Write-Host "Extracting to $pythonDir"
Expand-Archive -Path $zipPath -DestinationPath $pythonDir -Force

$pth = Get-ChildItem $pythonDir -Filter "python*._pth" | Select-Object -First 1
if ($pth) {
    $content = Get-Content $pth.FullName
    $content = $content | ForEach-Object {
        if ($_ -eq "#import site") { "import site" } else { $_ }
    }
    if ($content -notcontains "..\libs") {
        $content += "..\libs"
    }
    Set-Content -Path $pth.FullName -Value $content -Encoding ASCII
}

Write-Host "Python embeddable package installed in $pythonDir"
