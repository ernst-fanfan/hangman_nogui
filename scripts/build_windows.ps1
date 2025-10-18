Param(
    [string]$ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path)
)

$Root = (Resolve-Path (Join-Path $ProjectRoot "..")).Path
$DistRoot = Join-Path $Root "dist/windows"
$BuildRoot = Join-Path $Root "build/pyinstaller-windows"
$AppName = "Hangman"

Remove-Item $DistRoot, $BuildRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $DistRoot | Out-Null

python -m PyInstaller `
    (Join-Path $Root "scripts/run_hangman.py") `
    --name $AppName `
    --onefile `
    --clean `
    --collect-data english_words `
    --distpath (Join-Path $DistRoot "pyinstaller") `
    --workpath $BuildRoot `
    --specpath $BuildRoot

$ExePath = Join-Path $DistRoot ("pyinstaller\{0}.exe" -f $AppName)
if (-not (Test-Path $ExePath)) {
    Write-Error "Expected executable not found at $ExePath"
    exit 1
}

Write-Host "Built Windows executable at $ExePath"
