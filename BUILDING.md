# Building Native Bundles

These scripts produce reproducible binaries so CI can generate the artifacts without manual steps.

## Prerequisites

- Python 3.10+ with `pip`
- `pip install --upgrade build pyinstaller`
- macOS only: `brew install create-dmg`

## macOS (`.app` + `.dmg`)

```bash
./scripts/build_mac.sh
```

Results:

- PyInstaller bundle: `dist/mac/pyinstaller/Hangman.app`
- Disk image: `dist/mac/Hangman.dmg`

## Windows (`.exe`)

```powershell
pwsh -File scripts/build_windows.ps1
```

Result: `dist/windows/pyinstaller/Hangman.exe`

These scripts wipe `dist/mac`, `dist/windows`, and the corresponding `build/pyinstaller-*` directories to keep outputs deterministic. In CI, call the same scripts so every run matches local builds.
