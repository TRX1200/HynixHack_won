#!/usr/bin/env python3
"""Small entrypoint: query cards without loading the entire inventory into AI context."""
from pathlib import Path
import runpy
import sys

if sys.version_info < (3, 10):
    raise SystemExit('Python 3.10+ required; otherwise read field_inventory/catalog/README.md and only selected cards.')
runpy.run_path(str(Path(__file__).resolve().parents[1]/'field_inventory/tools/inventory.py'), run_name='__main__')
