#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
PYTHON="${PYTHON:-python3}"

"$PYTHON" -c '
import platform, sys
if sys.platform != "darwin" or platform.machine() != "arm64":
    sys.exit("Build on an Apple Silicon Mac using native ARM64 Python (disable Rosetta).")
if sys.version_info[:2] != (3, 11):
    sys.exit("Use CPython 3.11 for this pinned build environment; set PYTHON to its executable.")
'

"$PYTHON" -m venv .venv
PYTHON="$PROJECT_ROOT/.venv/bin/python"
export ARCHFLAGS="-arch arm64"
export MACOSX_DEPLOYMENT_TARGET=12.0
export MPLBACKEND=QtAgg
"$PYTHON" -m pip install -r requirements-macos-arm64.txt
export PATH="$PROJECT_ROOT/.venv/bin:$PATH"

"$PYTHON" setup.py build_ui
"$PYTHON" setup.py build_ext --inplace --force
PYTHONPATH="$PROJECT_ROOT" "$PYTHON" test/unit.py
"$PYTHON" -m PyInstaller --noconfirm --clean pyinstaller/macOneFile.spec
"$PYTHON" scripts/verify-macos-arm64.py dist/openMotor.app
/usr/bin/ditto -c -k --sequesterRsrc --keepParent dist/openMotor.app dist/openMotor-macos-arm64.zip
printf '\nBuilt: %s/dist/openMotor.app\nArchive: %s/dist/openMotor-macos-arm64.zip\n' "$PROJECT_ROOT" "$PROJECT_ROOT"
