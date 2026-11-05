#!/usr/bin/env python3
"""Generate a task-adaptive *validation plan*, never fabricate test results.

Each generated item is NOT_RUN until an actual validator and tests are executed.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('inventory',HERE/'inventory.py')
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

def create_contract(profile:dict)->dict:
    errors=mod.validate_profile(profile)
    if errors:raise ValueError('; '.join(errors))
    families=list(dict.fromkeys(profile.get('task_types',[])))
    tests=[]
    for family in families:
        plan=mod.FAMILY_ROUTINES[family]
        common={'family':family,'source':'REQUIRES SOURCE EVIDENCE','oracle':plan['oracle'],
                'status':'NOT_RUN','command':None,'test_log_path':None}
        for idx,action in enumerate(plan['positive'],1):
            tests.append({**common,'id':f'{family}:P{idx:02}','polarity':'positive','case':action})
        for idx,action in enumerate(plan['negative'],1):
            tests.append({**common,'id':f'{family}:N{idx:02}','polarity':'negative','case':action})
        tests.append({**common,'id':f'{family}:B01','polarity':'boundary',
                      'case':'Exercise the specified minimum/maximum or empty-input behavior; do not invent acceptance limits.'})
    for idx,hard in enumerate(profile.get('hard_constraints',[]),1):
        tests.append({'id':f'R{idx:03}','family':'requirements','polarity':'invariant',
                      'case':'Verify explicitly stated constraint: '+hard,
                      'source':'REQUIRES SOURCE LOCATION', 'oracle':'independent checker derived from raw data',
                      'status':'NOT_RUN','command':None,'test_log_path':None})
    return {
        'id':profile.get('id','unnamed'),
        'status':'PLAN_ONLY_NOT_VALIDATION',
        'purpose':'This scaffold is not a validator or pass proof. Implement independent checks and execute them.',
        'contract_fields_required':['input_schema','source_location','expected_behavior','test_command','evidence'],
        'unknowns':profile.get('unknowns',[]),
        'checks':tests,
        'summary':{'planned':len(tests),'passed':0,'failed':0,'not_run':len(tests)},
    }

def to_md(contract:dict)->str:
    lines=[f"# Task-specific validation plan: {contract['id']}",'',
           '**Status: PLAN ONLY — NOTHING TESTED**','',
           'Every row requires independent implementation, actual execution and evidence; missing tests remain `NOT_RUN`.','',
           '| ID | Family | Kind | Required case | Initial status |',
           '|---|---|---|---|---|']
    for t in contract['checks']:
        lines.append(f"| `{t['id']}` | {t['family']} | {t['polarity']} | {t['case'].replace('|','/')} | NOT_RUN |")
    lines+=['','## Unresolved']
    lines += [f'- {s}' for s in contract['unknowns']] or ['- None supplied; review missing information explicitly.']
    lines+=['','## Reviewer instructions','','For each test: record source evidence, independent expected value, code path, test command, exit status and log. Inject deliberate negative cases. Never change NOT_RUN to PASS based only on a model assertion.','']
    return '\n'.join(lines)

def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile',help='Path to a JSON problem profile')
    p.add_argument('--format',choices=['md','json'],default='md')
    p.add_argument('--out',default=None,help='Optional local output path; do not commit task-specific generated files to public Git')
    a=p.parse_args(argv)
    try:
        profile=mod.read_profile(a.profile)
        result=create_contract(profile)
    except (ValueError, OSError, json.JSONDecodeError) as ex:
        print(str(ex),file=sys.stderr);return 2
    text=(json.dumps(result,ensure_ascii=False,indent=2) if a.format=='json' else to_md(result))+'\n'
    if a.out:
        out=Path(a.out)
        if out.exists():print('Refusing to overwrite existing output',file=sys.stderr);return 3
        out.parent.mkdir(parents=True,exist_ok=True)
        try:
            with out.open('x',encoding='utf-8') as stream:stream.write(text)
        except FileExistsError:
            print('Refusing to overwrite existing output',file=sys.stderr);return 3
    else:print(text,end='')
    return 0
if __name__=='__main__':
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    sys.exit(main())
