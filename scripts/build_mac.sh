#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_ROOT="$ROOT/dist/mac"
BUILD_ROOT="$ROOT/build/pyinstaller-mac"
APP_NAME="Hangman"
APP_BUNDLE_NAME="${APP_NAME}.app"
DMG_NAME="${APP_NAME}.dmg"

rm -rf "$DIST_ROOT" "$BUILD_ROOT"
mkdir -p "$DIST_ROOT"

if [[ -f "$DIST_ROOT/$DMG_NAME" ]]; then
  echo "Removing existing disk image at $DIST_ROOT/$DMG_NAME"
  rm -f "$DIST_ROOT/$DMG_NAME"
fi

VOL_PATH="/Volumes/$APP_NAME"
if mount | grep -q "$VOL_PATH"; then
  echo "Unmounting $VOL_PATH"
  hdiutil detach "$VOL_PATH" || true
fi

python3 -m PyInstaller \
  "$ROOT/scripts/run_hangman.py" \
  --name "$APP_NAME" \
  --onedir \
  --clean \
  --collect-data english_words \
  --distpath "$DIST_ROOT/pyinstaller" \
  --workpath "$BUILD_ROOT" \
  --specpath "$BUILD_ROOT" \
  --osx-bundle-identifier "com.justernst.hangman"

if [[ -d "$DIST_ROOT/pyinstaller/$APP_BUNDLE_NAME" ]]; then
  APP_PATH="$DIST_ROOT/pyinstaller/$APP_BUNDLE_NAME"
else
  APP_PATH="$DIST_ROOT/pyinstaller/$APP_NAME"
fi

if [[ ! -e "$APP_PATH" ]]; then
  echo "Expected output not found at $DIST_ROOT/pyinstaller ($APP_BUNDLE_NAME or $APP_NAME)" >&2
  exit 1
fi

if ! command -v create-dmg >/dev/null 2>&1; then
  echo "create-dmg is required (install via Homebrew: brew install create-dmg)" >&2
  exit 1
fi

rm -f "$DIST_ROOT/$DMG_NAME"

if [[ -d "$APP_PATH" ]]; then
  create-dmg \
    --volname "$APP_NAME" \
    --window-size 500 280 \
    --icon-size 128 \
    --app-drop-link 380 160 \
    "$DIST_ROOT/$DMG_NAME" \
    "$APP_PATH"
else
  create-dmg \
    --volname "$APP_NAME" \
    --window-size 500 280 \
    --icon-size 128 \
    "$DIST_ROOT/$DMG_NAME" \
    "$APP_PATH"
fi

echo "Built macOS artifact at $APP_PATH"
echo "Created disk image at $DIST_ROOT/$DMG_NAME"
