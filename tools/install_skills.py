#!/usr/bin/env python3
"""Copy selected skill instructions into a permitted project. Never update Codex.

Does not touch AGENTS.md, global configuration, credentials or existing skills.
Use only after the host/assessment permits repository-local skill installation.
"""
from __future__ import annotations
import argparse
import re
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def install(project:Path,names:list[str])->list[str]:
    if not names or len(set(names)) != len(names):
        raise ValueError('Choose one or more distinct skill names; duplicates are refused before copying.')
    if not project.is_dir() or project.is_symlink() or any(p.is_symlink() for p in project.parents):
        raise ValueError('Existing non-symlink project directory required.')
    project=project.resolve()
    destinations=[]
    for name in names:
        if not re.fullmatch(r'wb-[a-z-]+',name):raise ValueError('Invalid skill name.')
        source=ROOT/'.agents'/'skills'/name
        if not (source/'SKILL.md').is_file():raise ValueError(f'Unknown skill: {name}')
        if source.is_symlink() or (source/'SKILL.md').is_symlink():
            raise ValueError('Symlink skill source refused.')
        dest=project/'.agents'/'skills'/name
        if dest.exists() or dest.is_symlink():raise ValueError(f'Refusing to overwrite {dest}.')
        if any(p.is_symlink() for p in dest.parents):raise ValueError('Symlink skill destination refused.')
        destinations.append((source,dest))
    license_source=ROOT/'LICENSE'
    if not license_source.is_file() or license_source.is_symlink():
        raise ValueError('Original toolkit LICENSE is required before copying any skills.')
    for source,dest in destinations:
        dest.mkdir(parents=True)
        text=(source/'SKILL.md').read_text(encoding='utf-8').replace('__KIT_ROOT__',ROOT.as_posix())
        (dest/'SKILL.md').write_text(text,encoding='utf-8')
        shutil.copyfile(license_source,dest/'LICENSE')
    return [str(d) for _,d in destinations]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--skills',nargs='+',required=True)
    args=p.parse_args()
    try:
        for path in install(args.project,args.skills):print(path)
        print('Check the provided Codex skill list. If unsupported, explicitly read SKILL.md. Do not upgrade Codex or bypass restrictions.')
        return 0
    except (ValueError,OSError) as e:print('ERROR:',e);return 2
if __name__=='__main__':raise SystemExit(main())
