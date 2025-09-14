#!/usr/bin/env bash
set -euo pipefail

FULL=0
if [[ "${1:-}" == "-f" || "${FULL:-0}" == "1" ]]; then
  FULL=1
fi

echo "[setup] Starting"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
backend="$repo_root/Backend"
venv="$backend/.venv-unix"

if [[ ! -d "$venv" ]]; then
  echo "[setup] Creating Unix venv at $venv"
  python3 -m venv "$venv"
else
  echo "[setup] Using existing venv: $venv"
fi

python="$venv/bin/python"
"$python" -m pip install -U pip wheel

echo "[setup] Installing dev requirements"
"$python" -m pip install -r "$backend/requirements-dev.txt"

if [[ "$FULL" == "1" ]]; then
  echo "[setup] Installing ML/heavy requirements"
  "$python" -m pip install -r "$backend/requirements-ml.txt"
fi

echo "[setup] Done. Activate: source $venv/bin/activate"
echo "[setup] Run tests: cd Backend && pytest -q -m 'not slow and not performance'"

