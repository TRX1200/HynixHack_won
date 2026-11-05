"""python -m workbench --help"""
from __future__ import annotations
import argparse
import csv
import importlib.util
import json
import platform
import sys
from pathlib import Path
from . import __version__
from .core import (json_text,write_new,load_json,profile_csv,join_audit,aggregate_csv,
                   solve_order,validate_evidence,inventory,check_manifest)


def main() -> int:
    # Structured CLI output is UTF-8 even when redirected under a legacy locale.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description='Offline evidence/workflow utilities. Explicit inputs; no API or browser use.')
    parser.add_argument('--version',action='version',version=__version__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('doctor'); p.add_argument('--out')
    p=sub.add_parser('calculate',help='Offline educational circuit/process formula calculator');p.add_argument('file');p.add_argument('--out')
    p=sub.add_parser('inventory'); p.add_argument('root'); p.add_argument('--out')
    p=sub.add_parser('csv-profile'); p.add_argument('file'); p.add_argument('--key',nargs='+',default=[])
    p.add_argument('--encoding',default='utf-8-sig');p.add_argument('--delimiter',default=',');p.add_argument('--out')
    p=sub.add_parser('join-audit');p.add_argument('left');p.add_argument('right');p.add_argument('--key',nargs='+',required=True)
    p.add_argument('--encoding',default='utf-8-sig');p.add_argument('--delimiter',default=',');p.add_argument('--out')
    p=sub.add_parser('aggregate');p.add_argument('file');p.add_argument('--group',nargs='*',default=[]);p.add_argument('--value',required=True)
    p.add_argument('--encoding',default='utf-8-sig');p.add_argument('--delimiter',default=',');p.add_argument('--out')
    p=sub.add_parser('extract');p.add_argument('files',nargs='+');p.add_argument('--out',required=True)
    p.add_argument('--lines',type=int,default=35);p.add_argument('--overlap',type=int,default=3);p.add_argument('--encoding',default='utf-8-sig')
    p=sub.add_parser('search');p.add_argument('index');p.add_argument('query');p.add_argument('--limit',type=int,default=5);p.add_argument('--source');p.add_argument('--out')
    p=sub.add_parser('read-chunk');p.add_argument('index');p.add_argument('id');p.add_argument('--out')
    p=sub.add_parser('check-evidence');p.add_argument('file');p.add_argument('--out')
    p=sub.add_parser('order');p.add_argument('file');p.add_argument('--out')
    p=sub.add_parser('assign');p.add_argument('file');p.add_argument('--max-states',type=int,default=100000);p.add_argument('--out')
    p=sub.add_parser('check-assignment');p.add_argument('spec');p.add_argument('assignment');p.add_argument('--out')
    p=sub.add_parser('check-manifest');p.add_argument('root');p.add_argument('file');p.add_argument('--out')
    p=sub.add_parser('contact-sheet');p.add_argument('files',nargs='+');p.add_argument('--image-out',required=True);p.add_argument('--out')
    p=sub.add_parser('crop');p.add_argument('file');p.add_argument('--box',nargs=4,type=int,required=True);p.add_argument('--image-out',required=True);p.add_argument('--out')
    p=sub.add_parser('annotate');p.add_argument('file');p.add_argument('regions');p.add_argument('--image-out',required=True);p.add_argument('--out')
    p=sub.add_parser('image-diff');p.add_argument('reference');p.add_argument('target');p.add_argument('--threshold',type=int,default=30);p.add_argument('--image-out',required=True);p.add_argument('--out')
    p=sub.add_parser('report');p.add_argument('file');p.add_argument('--format',choices=['md','html'],required=True);p.add_argument('--out',required=True)
    args=parser.parse_args();command=args.command
    try:
        # Check output collisions before expensive work. Never replace source/generated files silently.
        for name in ['out','image_out']:
            value=getattr(args,name,None)
            if value and Path(value).exists(): raise ValueError(f'Output exists: {value}. Choose a new path.')
        if command=='doctor':
            result={'toolkit':__version__,'python':platform.python_version(),'platform':platform.system(),
                    'python_supported':sys.version_info>=(3,10),
                    'optional_modules':{n:importlib.util.find_spec(n) is not None for n in ['PIL','fitz']},
                    'scope':'No secrets, environment values, personal config or network are inspected. Codex is not changed.'}
        elif command=='calculate':
            from .electronics import calculate
            result=calculate(load_json(args.file))
        elif command=='inventory': result=inventory(args.root)
        elif command=='csv-profile': result=profile_csv(args.file,args.key,args.encoding,args.delimiter)
        elif command=='join-audit': result=join_audit(args.left,args.right,args.key,args.encoding,args.delimiter)
        elif command=='aggregate': result=aggregate_csv(args.file,args.group,args.value,args.encoding,args.delimiter)
        elif command=='extract':
            from .documents import extract_to_index
            result=extract_to_index(args.files,args.out,args.lines,args.overlap,args.encoding)
        elif command in ['search','read-chunk']:
            from .documents import load_index,search_chunks,get_chunk
            data=load_index(args.index)
            result=search_chunks(data,args.query,args.limit,args.source) if command=='search' else get_chunk(data,args.id)
        elif command=='check-evidence': result=validate_evidence(load_json(args.file))
        elif command=='order': result=solve_order(load_json(args.file))
        elif command in ['assign','check-assignment']:
            from .optimization import solve_assignment,validate_assignment
            result=solve_assignment(load_json(args.file),args.max_states) if command=='assign' else validate_assignment(load_json(args.spec),load_json(args.assignment))
        elif command=='check-manifest': result=check_manifest(args.root,load_json(args.file))
        elif command in ['contact-sheet','crop','annotate','image-diff']:
            from .images import contact_sheet,crop_image,annotate,difference
            if command=='contact-sheet': result=contact_sheet(args.files,args.image_out)
            elif command=='crop': result=crop_image(args.file,args.box,args.image_out)
            elif command=='annotate': result=annotate(args.file,load_json(args.regions),args.image_out)
            else: result=difference(args.reference,args.target,args.image_out,args.threshold)
        elif command=='report':
            from .reporting import render_report
            result=render_report(load_json(args.file),args.out,args.format)
        else: raise ValueError('Unsupported command.')
        if getattr(args,'out',None) and command not in ['extract','report']:
            write_new(args.out,json_text(result))
        print(json_text(result))
        failed=(result.get('structural_valid') is False or result.get('all_passed') is False or result.get('feasible') is False)
        return 1 if failed else 0
    except (ValueError,OSError,UnicodeError,KeyError,TypeError,ImportError,csv.Error,json.JSONDecodeError) as exc:
        print(json_text({'error':str(exc),'command':command,'partial_result_must_not_be_treated_as_success':True}),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
