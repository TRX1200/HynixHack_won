#!/usr/bin/env python3
"""Report candidate package metadata. No installation, imports of candidates or network."""
from __future__ import annotations
import importlib.metadata as metadata
import json
import platform
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def main() -> int:
    catalog = json.loads((ROOT / 'catalog/libraries.json').read_text(encoding='utf-8'))
    packages = []
    for item in catalog['libraries']:
        version = None
        if item['ecosystem'] == 'pypi':
            try:
                version = metadata.version(item['package'])
            except metadata.PackageNotFoundError:
                pass
        packages.append({'package': item['package'], 'ecosystem': item['ecosystem'],
                         'installed_version': version,
                         'note': 'metadata only; no compatibility or import test'})
    print(json.dumps({'python': platform.python_version(), 'os': platform.system(),
                      'node_on_path': shutil.which('node') is not None,
                      'packages': packages}, ensure_ascii=False, indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
