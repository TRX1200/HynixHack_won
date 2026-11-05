#!/usr/bin/env python3
"""Run the toolkit without pip install and without changing the current directory."""
import sys
from pathlib import Path
if sys.version_info < (3, 10):
    print('Python 3.10+ is required for these utilities. SKILL.md files can still be read without Python.', file=sys.stderr)
    raise SystemExit(2)
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workbench.__main__ import main
if __name__=='__main__':raise SystemExit(main())
