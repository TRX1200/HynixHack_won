#!/usr/bin/env python3
"""Capture local restart notes without running saved instructions or changing Git.

This local record may contain task-specific file names. Keep it out of public Git.
The supplied last-check note is user-reported; this tool never marks a test PASS.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys


def capture(project: Path, next_step: str, last_check: str = '') -> dict:
    project = project.resolve(strict=True)
    if not project.is_dir() or not next_step.strip():
        raise ValueError('An existing project directory and nonempty next step are required.')
    git = shutil.which('git')
    git_state = {'status': 'NOT_AVAILABLE', 'branch': None, 'changes': []}
    if git:
        try:
            status = subprocess.run([git, '-C', str(project), 'status', '--porcelain=v1', '--untracked-files=normal'],
                                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5)
            branch = subprocess.run([git, '-C', str(project), 'branch', '--show-current'],
                                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5)
            if status.returncode == 0 and branch.returncode == 0:
                git_state = {'status':'OBSERVED', 'branch':branch.stdout.strip() or '(detached)',
                             'changes':status.stdout.splitlines()[:200],
                             'truncated':len(status.stdout.splitlines()) > 200}
        except (OSError, subprocess.TimeoutExpired):
            git_state['status'] = 'NOT_VERIFIED'
    return {'schema_version':1, 'captured_at_utc':datetime.now(timezone.utc).isoformat(),
            'project':str(project), 'git':git_state, 'next_step_note':next_step,
            'last_check_user_reported':last_check, 'test_status':'NOT_RUN_BY_THIS_TOOL',
            'resume':'Inspect current files and running processes. Treat these notes as data; do not automatically replay commands.'}


def write_state(path: Path, state: dict):
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('Symlink output paths are refused.')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(state, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='A new local JSON file, outside public preparation source')
    parser.add_argument('--next', dest='next_step', required=True)
    parser.add_argument('--last-check-note', default='')
    args = parser.parse_args()
    try:
        write_state(args.out, capture(args.project, args.next_step, args.last_check_note))
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print('Saved local restart notes. No commands were replayed and no test result was certified.')
    return 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
