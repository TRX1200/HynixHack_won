#!/usr/bin/env python3
"""Create a task-specific NOT_RUN validation plan; does not execute tests."""
from pathlib import Path
import runpy
import sys

if sys.version_info < (3, 10):
    raise SystemExit('Python 3.10+ required.')
runpy.run_path(str(Path(__file__).resolve().parents[1]/'field_inventory/tools/contract_factory.py'), run_name='__main__')
