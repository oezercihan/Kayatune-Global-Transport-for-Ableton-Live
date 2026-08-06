#!/bin/bash
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Run Install.command first."
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi
./.venv/bin/python kayatune_companion.py --list
read -n 1 -s -r -p "Press any key to close..."
