Param(
  [switch]$Full
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[setup] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[setup] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[setup] $msg" -ForegroundColor Yellow }

$repoRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $repoRoot "Backend"
$venv = Join-Path $backend ".venv-win"

if (-not (Test-Path $venv)) {
  Write-Info "Creating Windows venv at $venv"
  py -3 -m venv $venv
} else {
  Write-Info "Using existing venv: $venv"
}

$python = Join-Path $venv "Scripts/python.exe"
& $python -m pip install -U pip wheel

Write-Info "Installing dev requirements"
& $python -m pip install -r (Join-Path $backend "requirements-dev.txt")

if ($Full) {
  Write-Info "Installing ML/heavy requirements"
  & $python -m pip install -r (Join-Path $backend "requirements-ml.txt")
}

Write-Ok "Done. Activate with: `n  .\\Backend\\.venv-win\\Scripts\\Activate.ps1"
Write-Ok "Run tests:       `n  cd Backend; pytest -q -m 'not slow and not performance'"

