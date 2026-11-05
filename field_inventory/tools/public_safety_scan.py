#!/usr/bin/env python3
"""Best-effort static scan; NEVER a guarantee that publication is safe."""
from pathlib import Path
import argparse
import re
import sys
BASE=Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES=('PRIVATE_CONTEXT','DO_NOT_PUBLISH','actual_exam','secret_key','credentials.json')
SUSPICIOUS_CONTENT=(
    re.compile(r'-----BEGIN [A-Z ]+PRIVATE KEY-----'),
    re.compile(r'(?i)(?:api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\']?[a-z0-9_-]{20,}'),
)

def scan(root:Path)->list[str]:
    issues=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if any(w.casefold() in str(rel).casefold() for w in FORBIDDEN_NAMES):
            issues.append('sensitive path: '+str(rel))
        if p.is_file() and p.suffix.lower() in ('.md','.txt','.json','.py','.js','.csv','.toml','.yaml','.yml'):
            try:content=p.read_text(encoding='utf-8')
            except UnicodeDecodeError:continue
            for rgx in SUSPICIOUS_CONTENT:
                if rgx.search(content):issues.append('suspected secret: '+str(rel))
    return issues

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',nargs='?',default=str(BASE))
    args=parser.parse_args()
    root=Path(args.root).resolve()
    errs=scan(root)
    print('WARN: heuristic scan only; human diff review required')
    for err in errs:print('FLAG:',err)
    print('FOUND',len(errs),'flags')
    sys.exit(1 if errs else 0)
