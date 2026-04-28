#!/bin/bash
# Crea RaxeusAI.app sul Desktop (macOS)
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="RaxeusAI"
APP_BUNDLE="$HOME/Desktop/${APP_NAME}.app"
LOGO="$PROJECT_DIR/static/logo.png"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"

echo "=== Creazione RaxeusAI.app ==="

# ── 1. Icona ─────────────────────────────────────────────────────────────────
echo "[1/3] Generazione icona..."

ICONSET_DIR="$PROJECT_DIR/AppIcon.iconset"
SQUARE_TMP="$PROJECT_DIR/_logo_square_tmp.png"

# Crop quadrato centrato (logo 1004x1027 → 1004x1004)
sips --cropOffset 0 11 --cropToHeightWidth 1004 1004 "$LOGO" --out "$SQUARE_TMP" > /dev/null 2>&1

mkdir -p "$ICONSET_DIR"
for SIZE in 16 32 64 128 256 512; do
    sips -z $SIZE $SIZE "$SQUARE_TMP" --out "$ICONSET_DIR/icon_${SIZE}x${SIZE}.png" > /dev/null 2>&1
done
sips -z 32   32   "$SQUARE_TMP" --out "$ICONSET_DIR/icon_16x16@2x.png"   > /dev/null 2>&1
sips -z 64   64   "$SQUARE_TMP" --out "$ICONSET_DIR/icon_32x32@2x.png"   > /dev/null 2>&1
sips -z 256  256  "$SQUARE_TMP" --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null 2>&1
sips -z 512  512  "$SQUARE_TMP" --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null 2>&1
sips -z 1024 1024 "$SQUARE_TMP" --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null 2>&1

iconutil -c icns "$ICONSET_DIR" -o "$PROJECT_DIR/AppIcon.icns"
rm -rf "$ICONSET_DIR" "$SQUARE_TMP"
echo "    Icona creata."

# ── 2. Bundle .app ────────────────────────────────────────────────────────────
echo "[2/3] Costruzione .app bundle..."

# Rimuovi vecchia versione se presente
[ -d "$APP_BUNDLE" ] && rm -rf "$APP_BUNDLE"

mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Icona
cp "$PROJECT_DIR/AppIcon.icns" "$APP_BUNDLE/Contents/Resources/AppIcon.icns"

# Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>RaxeusAI</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.raxeus.ai</string>
    <key>CFBundleName</key>
    <string>RaxeusAI</string>
    <key>CFBundleDisplayName</key>
    <string>RaxeusAI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsLocalNetworking</key>
        <true/>
    </dict>
</dict>
</plist>
PLIST

# Script di avvio
cat > "$APP_BUNDLE/Contents/MacOS/RaxeusAI" << LAUNCHER
#!/bin/bash
cd "$PROJECT_DIR"
exec "$PYTHON_PATH" "$PROJECT_DIR/launcher.py"
LAUNCHER

chmod +x "$APP_BUNDLE/Contents/MacOS/RaxeusAI"

# ── 3. Registra con il sistema ────────────────────────────────────────────────
echo "[3/3] Registrazione app..."
touch "$APP_BUNDLE"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
    -f "$APP_BUNDLE" > /dev/null 2>&1 || true

echo ""
echo "✓ RaxeusAI.app creato sul Desktop!"
echo "  Prima apertura: tasto destro → Apri (per aggirare Gatekeeper)"
echo "  Le volte successive: doppio click normalmente."
