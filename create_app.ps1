# Crea RaxeusAI.exe sul Desktop (Windows) usando PyInstaller.
# Uso: powershell -ExecutionPolicy Bypass -File .\create_app.ps1
$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppName    = "RaxeusAI"
$Desktop    = [Environment]::GetFolderPath("Desktop")
$DistDir    = Join-Path $ProjectDir "dist"
$BuildDir   = Join-Path $ProjectDir "build"
$Logo       = Join-Path $ProjectDir "static\logo.png"
$Icon       = Join-Path $ProjectDir "AppIcon.ico"
$Venv       = Join-Path $ProjectDir "venv\Scripts"
$PythonExe  = Join-Path $Venv "python.exe"

Write-Host "=== Creazione RaxeusAI.exe ===" -ForegroundColor Cyan

if (-Not (Test-Path $PythonExe)) {
    Write-Host "× venv non trovato. Crea prima l'ambiente:" -ForegroundColor Red
    Write-Host "    python -m venv venv"
    Write-Host "    .\venv\Scripts\activate"
    Write-Host "    pip install -r requirements.txt"
    exit 1
}

# 1. Icona ICO ────────────────────────────────────────────────────────────────
Write-Host "[1/3] Generazione icona ICO..."
& $PythonExe -c @"
from PIL import Image
import os
src = r'$Logo'
dst = r'$Icon'
img = Image.open(src).convert('RGBA')
w, h = img.size
side = min(w, h)
left = (w - side) // 2
top = max(0, (h - side) // 2)
img = img.crop((left, top, left + side, top + side))
img.save(dst, format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('Icona generata:', dst)
"@

# 2. PyInstaller ──────────────────────────────────────────────────────────────
Write-Host "[2/3] Build con PyInstaller..."
& $PythonExe -m pip install --quiet --upgrade pyinstaller pillow

if (Test-Path $DistDir)  { Remove-Item -Recurse -Force $DistDir }
if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }

& $PythonExe -m PyInstaller `
    --noconfirm `
    --windowed `
    --name $AppName `
    --icon $Icon `
    --add-data "templates;templates" `
    --add-data "static;static" `
    --hidden-import "openai" `
    --hidden-import "flask" `
    --hidden-import "webview" `
    --hidden-import "chromadb" `
    --hidden-import "pypdf" `
    --hidden-import "ddgs" `
    --hidden-import "googlesearch" `
    --hidden-import "yt_dlp" `
    "$ProjectDir\launcher.py"

# 3. Copia su Desktop ─────────────────────────────────────────────────────────
Write-Host "[3/3] Copia su Desktop..."
$Built = Join-Path $DistDir $AppName
$Dest  = Join-Path $Desktop $AppName

if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
Copy-Item -Recurse $Built $Dest

Write-Host ""
Write-Host "✓ $AppName.exe creato su: $Dest" -ForegroundColor Green
Write-Host "  Doppio click su $Dest\$AppName.exe per avviare."
