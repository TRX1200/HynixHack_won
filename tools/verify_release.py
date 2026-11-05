#!/usr/bin/env python3
"""Verify the exact public package against its release manifest.

Not a secret scanner, legal approval or protection against malicious manifest edits.
Prepare-only publishing should copy only verified listed files, never a workspace.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def verify(root:Path=ROOT)->list[str]:
    manifest=root/'RELEASE_MANIFEST.json'
    data=json.loads(manifest.read_text(encoding='utf-8'))
    errors=[]; expected=set()
    for item in data['files']:
        rel=item['path'];p=root/rel
        if rel in expected:errors.append('Duplicate manifest path: '+rel)
        expected.add(rel)
        if not p.resolve().is_relative_to(root.resolve()) or p.is_symlink() or any(x.is_symlink() for x in p.parents):
            errors.append('Unsafe path: '+rel);continue
        if not p.is_file():errors.append('Missing file: '+rel);continue
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest!=item['sha256'] or p.stat().st_size!=item['bytes']:errors.append('Changed file: '+rel)
    actual=set()
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if '.git' in rel.parts or '__pycache__' in rel.parts or p.suffix=='.pyc':continue
        if p.is_file() and rel.as_posix() not in {'RELEASE_MANIFEST.json','toolkit-source.zip','CHECKSUMS.sha256'}:actual.add(rel.as_posix())
    for rel in sorted(actual-expected):errors.append('Unexpected file (do not publish): '+rel)
    archive=root/'toolkit-source.zip'
    checksums=root/'CHECKSUMS.sha256'
    if archive.exists() or checksums.exists():
        if not archive.is_file() or not checksums.is_file() or archive.is_symlink() or checksums.is_symlink():
            errors.append('Distribution archive and CHECKSUMS.sha256 must both be ordinary files.')
        else:
            wanted=checksums.read_text(encoding='utf-8').strip().split()
            digest=hashlib.sha256(archive.read_bytes()).hexdigest()
            if wanted!=[digest,'toolkit-source.zip']:errors.append('Distribution ZIP checksum mismatch.')
    return errors

if __name__=='__main__':
    try:
        errors=verify()
        print(json.dumps({'verified':not errors,'errors':errors},ensure_ascii=False,indent=2))
        raise SystemExit(1 if errors else 0)
    except (OSError,ValueError,KeyError) as e:
        print(json.dumps({'verified':False,'error':str(e)},ensure_ascii=False));raise SystemExit(2)
