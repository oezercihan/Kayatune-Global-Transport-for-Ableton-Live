#!/bin/bash
set -e
cd "$(dirname "$0")"
PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3 was not found. Install Python 3 from python.org first."
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi
"$PYTHON_BIN" -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install "mido==1.3.3" "python-rtmidi==1.5.8"
echo
echo "Installation complete. Start with Start.command"
read -n 1 -s -r -p "Press any key to close..."
