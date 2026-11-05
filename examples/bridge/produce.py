#!/usr/bin/env python3
"""Convert a small explicit JSON input and print strict JSON. Logs go to stderr."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workbench.contracts import load_json, convert_temperature

MAX_BYTES = 2_000_000

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--output', type=Path, help='New file only; default is stdout')
    a = p.parse_args()
    try:
        if not a.input.is_file() or a.input.stat().st_size > MAX_BYTES:
            raise ValueError('Input must be a regular JSON file no larger than 2 MB.')
        result = convert_temperature(load_json(a.input.read_text(encoding='utf-8')))
        text = json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
        if a.output:
            if a.output.is_symlink() or any(x.is_symlink() for x in a.output.parents):
                raise ValueError('Symlink output refused.')
            with a.output.open('x', encoding='utf-8') as f:
                f.write(text)
            print('Created validated example output.', file=sys.stderr)
        else:
            sys.stdout.write(text)
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
if __name__ == '__main__':
    raise SystemExit(main())
