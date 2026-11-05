#!/usr/bin/env python3
"""Build a host-mergeable MCP JSON example using real local paths.

This command validates the explicitly selected index but never registers a server,
edits host settings, starts a process, installs a package, or sends any data.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def build_config(index: Path) -> dict:
    from workbench.core import checked_file
    from workbench.documents import load_index

    selected = checked_file(index).resolve()
    records = load_index(selected)
    if not records:
        raise ValueError('The selected index is empty. Extract a small local document first.')
    server = ROOT / 'mcp' / 'local_evidence_server.py'
    if not server.is_file() or server.is_symlink():
        raise ValueError('The toolkit MCP server source is missing or is a symlink.')
    if not sys.executable:
        raise ValueError('Unable to determine the current Python executable.')
    return {
        'mcpServers': {
            'local-evidence': {
                'command': str(Path(sys.executable).resolve()),
                'args': [str(server.resolve()), '--index', str(selected)],
            }
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, required=True, help='Existing nonempty JSONL evidence index')
    parser.add_argument('--out', type=Path, help='Optional new JSON file; existing files are refused')
    args = parser.parse_args()
    try:
        if sys.version_info < (3, 10):
            raise ValueError('Python 3.10+ is required for the local MCP server.')
        if args.out and (args.out.exists() or args.out.is_symlink()):
            raise ValueError('Output exists. Choose a new file; host configuration is never overwritten.')
        config = build_config(args.index)
        # ASCII escaping keeps redirected output valid even under non-UTF-8 Windows locales.
        text = json.dumps(config, indent=2, ensure_ascii=True) + '\n'
        if args.out:
            from workbench.core import write_new
            write_new(args.out, text)
        sys.stdout.write(text)
        return 0
    except (ValueError, OSError, UnicodeError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
