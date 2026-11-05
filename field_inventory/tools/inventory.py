#!/usr/bin/env python3
"""Offline task -> capability/validation planning aid. No network, no writes.

This is a *heuristic retrieval helper*, not a semantic planner or an executable solver.
"""
from __future__ import annotations
import argparse
from collections import Counter
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

BASE = Path(__file__).resolve().parents[1]
CATALOG = BASE / 'catalog' / 'capabilities.json'
DECISIONS = BASE / 'catalog' / 'decision_rules.json'
CODE_PATTERNS = BASE / 'catalog' / 'code_patterns.json'
ALIASES = BASE / 'catalog' / 'korean_aliases.json'
VALID_TYPES = {
    'web_app', 'data_pipeline', 'optimization', 'statistics_ml',
    'computer_vision', 'scientific_computing', 'documents_search',
    'geospatial', 'reporting', 'integration', 'quality_security',
}
FAMILY_ROUTINES = {
    'web_app': {
        'contract': ['UI input/output schema', 'API request/response codes', 'authentication/authorization if applicable'],
        'positive': ['browser action -> real API -> computation -> rendered result'],
        'negative': ['invalid JSON/input', 'unauthorized role for protected mutation', 'empty state'],
        'oracle': 'Manual UI walkthrough + independent HTTP contract test',
    },
    'data_pipeline': {
        'contract': ['source keys and grain', 'join cardinality', 'missing-value policy', 'idempotence'],
        'positive': ['raw input -> expected records and aggregation'],
        'negative': ['duplicate join key', 'missing lookup key', 'empty file or malformed encoding'],
        'oracle': 'Independent parse and count/key conservation',
    },
    'optimization': {
        'contract': ['decision variables', 'objective sense/units', 'hard constraints', 'time/quality budget'],
        'positive': ['nonempty known-feasible synthetic case'],
        'negative': ['infeasible capacity/coverage', 'duplicate item', 'asymmetric cost matrix'],
        'oracle': 'Independent constraint checker + tiny exact oracle when possible',
    },
    'statistics_ml': {
        'contract': ['sampling unit', 'target/label availability', 'split rule', 'metric and uncertainty'],
        'positive': ['seeded synthetic data with known relationship'],
        'negative': ['label leakage', 'single-class split', 'temporal order leakage'],
        'oracle': 'Holdout/walk-forward metrics + no-skill baseline',
    },
    'computer_vision': {
        'contract': ['pixel coordinate system', 'registration/calibration', 'ground truth status'],
        'positive': ['known marked or synthetic shape'],
        'negative': ['shift-only unchanged image', 'contrast-only difference', 'wrong scale'],
        'oracle': 'Known-mask/pixel landmark comparison; visual review',
    },
    'scientific_computing': {
        'contract': ['governing equations', 'unit system', 'initial/boundary conditions', 'tolerances'],
        'positive': ['analytic/manufactured solution with known result'],
        'negative': ['unit mismatch', 'wrong sign', 'coarse step instability'],
        'oracle': 'Independent residual + convergence and limit checks',
    },
    'documents_search': {
        'contract': ['source location', 'version/date applicability', 'citation precision'],
        'positive': ['known clause retrieved and cited'],
        'negative': ['similar obsolete clause', 'missing clause', 'contradictory language'],
        'oracle': 'Open exact original source offset/page',
    },
    'geospatial': {
        'contract': ['CRS/lat-lon convention', 'distance model', 'directionality and units'],
        'positive': ['known coordinate pair and permitted travel matrix'],
        'negative': ['swapped lat/lon', 'unreachable or obstacle-separated points'],
        'oracle': 'Known geometry + supplied matrix validation',
    },
    'reporting': {
        'contract': ['claim-to-source mapping', 'figures/units', 'export format'],
        'positive': ['number re-derived from supplied synthetic data'],
        'negative': ['unlinked claim', 'broken font', 'mismatched summary figure'],
        'oracle': 'Independent computation plus output artifact visual inspection',
    },
    'integration': {
        'contract': ['schema version', 'ID representation', 'null/unit/error contract'],
        'positive': ['versioned payload roundtrip'],
        'negative': ['missing required field', 'unit mismatch', 'duplicate retried action'],
        'oracle': 'Producer-consumer contract and idempotency tests',
    },
    'quality_security': {
        'contract': ['permissions, allowed runtime', 'secret and publication scope'],
        'positive': ['expected permitted operation'],
        'negative': ['unauthorized server mutation', 'synthetic secret canary', 'crash recovery'],
        'oracle': 'Independent security/negative-case tests and diff review',
    },
}


MAX_JSON_BYTES = 4 * 1024 * 1024
ID_RE = re.compile(r'[a-z][a-z0-9-]{0,79}\Z')

def _json_tree_errors(value: Any, path: str = '$', depth: int = 0) -> list[str]:
    if depth > 16:return [path + ': nesting exceeds 16 levels']
    if value is None or type(value) in (str, bool, int):return []
    if type(value) is float:return [] if math.isfinite(value) else [path + ': non-finite number']
    if type(value) is list:
        if len(value) > 1000:return [path + ': list exceeds 1000 items']
        return [e for i,item in enumerate(value) for e in _json_tree_errors(item,f'{path}[{i}]',depth+1)]
    if type(value) is dict:
        if len(value) > 200:return [path + ': object exceeds 200 fields']
        errors=[]
        for key,item in value.items():
            if type(key) is not str:errors.append(path + ': object keys must be strings')
            else:errors += _json_tree_errors(item,path+'.'+key,depth+1)
        return errors
    return [path + ': only JSON types are accepted']

def read_json(path: str | Path, *, internal: bool = False) -> Any:
    p=Path(path).expanduser()
    if p.is_symlink() or any(parent.is_symlink() for parent in p.parents):
        raise ValueError('Symbolic-link JSON paths are not accepted')
    p=p.resolve(strict=True)
    if internal and not p.is_relative_to(BASE.resolve()):raise ValueError('Catalog path escapes inventory root')
    if not p.is_file() or p.stat().st_size > MAX_JSON_BYTES:
        raise ValueError('JSON input must be a regular file of at most 4 MiB')
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('Duplicate JSON key: '+key)
            out[key]=value
        return out
    def bad_constant(value):raise ValueError('Non-finite JSON constant: '+value)
    def finite_float(value):
        number=float(value)
        if not math.isfinite(number):raise ValueError('JSON numeric overflow')
        if number==0 and any(ch in '123456789' for ch in value.split('e')[0].split('E')[0]):
            raise ValueError('JSON numeric underflow')
        return number
    try:
        result=json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=unique,
                          parse_constant=bad_constant,parse_float=finite_float)
    except RecursionError as exc:raise ValueError('JSON nesting exceeds supported limit') from exc
    errors=_json_tree_errors(result)
    if errors:raise ValueError('; '.join(errors))
    return result

def _schema_errors(value: Any, schema: dict, path: str = '$') -> list[str]:
    if type(schema) is not dict:return [path+': invalid schema definition']
    typ=schema.get('type')
    valid={'object':type(value) is dict,'array':type(value) is list,'string':type(value) is str,
           'boolean':type(value) is bool,'integer':type(value) is int,'number':type(value) in (int,float)}
    if typ and not valid.get(typ,False):return [f'{path}: expected {typ}']
    errors=[]
    if 'enum' in schema and not any(type(value) is type(x) and value==x for x in schema['enum']):
        errors.append(f'{path}: unsupported value {value!r}')
    if typ=='object':
        properties=schema.get('properties',{})
        for key in schema.get('required',[]):
            if key not in value:errors.append(f'{path}: missing {key}')
        for key,item in value.items():
            if key in properties:errors+=_schema_errors(item,properties[key],path+'.'+str(key))
            elif schema.get('additionalProperties') is False:
                errors.append(f'{path}: unknown field {key!r}; put unresolved facts in unknowns')
    elif typ=='array':
        if len(value)>schema.get('maxItems',1000):errors.append(f'{path}: too many items')
        if schema.get('uniqueItems'):
            seen=set()
            for item in value:
                marker=json.dumps(item,sort_keys=True,allow_nan=False)
                if marker in seen:
                    errors.append(f'{path}: duplicate items');break
                seen.add(marker)
        for index,item in enumerate(value):
            errors+=_schema_errors(item,schema.get('items',{}),f'{path}[{index}]')
    elif typ=='string':
        if (len(value)<schema.get('minLength',0) or len(value)>schema.get('maxLength',40000)
                or (schema.get('minLength',0)>0 and not value.strip())):
            errors.append(f'{path}: invalid string length')
    elif typ in ('number','integer'):
        try:
            if not math.isfinite(value):errors.append(f'{path}: non-finite number')
            if 'minimum' in schema and value<schema['minimum']:errors.append(f'{path}: below minimum')
            if 'exclusiveMinimum' in schema and value<=schema['exclusiveMinimum']:errors.append(f'{path}: must be positive')
        except OverflowError:errors.append(f'{path}: number exceeds supported range')
    return errors

def validate_profile(profile: Any) -> list[str]:
    errors=_json_tree_errors(profile)
    if errors:return errors
    return _schema_errors(profile,read_json(BASE/'schemas/problem_profile.schema.json',internal=True))

def read_profile(path: str | Path) -> dict:
    profile=read_json(path);errors=validate_profile(profile)
    if errors:raise ValueError('; '.join(errors))
    return profile

def _strings(value: Any, *, allow_empty: bool = False) -> bool:
    return (type(value) is list and (allow_empty or bool(value))
            and all(type(x) is str and bool(x.strip()) and len(x)<=40000 for x in value)
            and len(value)==len(set(value)))

def _collection(path: Path, key: str) -> list[dict]:
    raw=read_json(path,internal=True)
    if type(raw) is not dict or set(raw)-{'version','schema_version','note',key}:
        raise ValueError(f'{path.name}: invalid catalog envelope')
    if type(raw.get('version')) is not str or not raw['version'].strip():raise ValueError(f'{path.name}: version required')
    if 'schema_version' in raw and type(raw['schema_version']) is not int:
        raise ValueError(f'{path.name}: schema_version must be integer, not bool')
    if key=='capabilities' and (type(raw.get('schema_version')) is not int or raw['schema_version']!=1):
        raise ValueError(f'{path.name}: capability schema_version must be 1')
    if 'note' in raw and type(raw['note']) is not str:raise ValueError(f'{path.name}: note must be string')
    rows=raw.get(key)
    if type(rows) is not list or not rows or len(rows)>1000:raise ValueError(f'{path.name}: {key} must contain 1..1000 objects')
    if any(type(row) is not dict for row in rows):raise ValueError(f'{path.name}: every entry must be an object')
    return rows

def validate_catalog(cards: Any) -> list[str]:
    if type(cards) is not list or not cards or len(cards)>1000:return ['capabilities must be a list of 1..1000 objects']
    errors,ids=[],set()
    fields={'id','family','task_types','title','signals','baseline','upgrade','verification','libraries','fallback','warning','implementation_status','verified_commands'}
    for index,card in enumerate(cards):
        if type(card) is not dict:
            errors.append(f'card {index}: must be object');continue
        ident=card.get('id')
        if type(ident) is not str or not ID_RE.fullmatch(ident):
            errors.append('bad id: '+repr(ident));continue
        if ident in ids:errors.append('duplicate id: '+ident)
        ids.add(ident)
        if set(card)-fields:errors.append(f'{ident}: unknown fields')
        if card.get('implementation_status') not in ('RECIPE_ONLY','IMPLEMENTED','TESTED'):
            errors.append(f'{ident}: unknown implementation_status')
        for key in ('family','title','baseline','upgrade','verification','fallback','warning'):
            if type(card.get(key)) is not str or not card[key].strip() or len(card[key])>40000:
                errors.append(f'{ident}: missing {key}')
        if type(card.get('family')) is not str or card['family'] not in {'algorithms','data','orchestration','quality','report','science','statistics','vision','web'}:
            errors.append(f'{ident}: unknown family')
        for key in ('task_types','signals','libraries'):
            if not _strings(card.get(key)):errors.append(f'{ident}: invalid {key}')
        if type(card.get('task_types')) is list and any(type(kind) is not str or kind not in VALID_TYPES|{'all'} for kind in card['task_types']):
            errors.append(f'{ident}: unknown task type')
        if not _strings(card.get('verified_commands'),allow_empty=True):
            errors.append(f'{ident}: invalid verified_commands')
        elif card.get('implementation_status')=='RECIPE_ONLY' and card['verified_commands']:
            errors.append(f'{ident}: RECIPE_ONLY cannot claim verified commands')
        elif card.get('implementation_status')=='TESTED' and not card['verified_commands']:
            errors.append(f'{ident}: TESTED needs reproducible verified_commands')
        recipe=BASE/'recipes'/(ident+'.md')
        if (recipe.is_symlink() or any(parent.is_symlink() for parent in recipe.parents)
                or not recipe.is_file() or not recipe.resolve().is_relative_to(BASE.resolve())):
            errors.append(f'{ident}: missing recipe or unsafe recipe path')
    if not (BASE/'docs/VALIDATOR_BY_PROBLEM.md').is_file():errors.append('missing validator plan')
    return errors

def load_catalog() -> list[dict[str, Any]]:
    cards=_collection(CATALOG,'capabilities');errors=validate_catalog(cards)
    if errors:raise ValueError('; '.join(errors))
    return cards

def _asset_rows(cards: list[dict]) -> tuple[list[dict],list[dict],list[dict]]:
    ids={card['id'] for card in cards}
    rules=_collection(DECISIONS,'rules');patterns=_collection(CODE_PATTERNS,'patterns');aliases=_collection(ALIASES,'aliases')
    seen=set()
    property_schema=read_json(BASE/'schemas/problem_profile.schema.json',internal=True)['properties']['properties']
    for rule in rules:
        if set(rule)!={'id','when','recommend','avoid','explanation'}:raise ValueError('Decision rule fields must be exact')
        ident=rule['id']
        if type(ident) is not str or not ID_RE.fullmatch(ident) or ident in seen:raise ValueError('Invalid or duplicate rule ID')
        seen.add(ident)
        if type(rule['when']) is not dict or not rule['when'] or _schema_errors(rule['when'],property_schema):
            raise ValueError(ident+': invalid condition types or properties')
        for key in ('recommend','avoid'):
            if not _strings(rule[key],allow_empty=True) or set(rule[key])-ids:
                raise ValueError(ident+': unknown or invalid capability references')
        if set(rule['recommend'])&set(rule['avoid']):raise ValueError(ident+': same capability both recommended and avoided')
        if type(rule['explanation']) is not str or not rule['explanation'].strip():raise ValueError(ident+': explanation required')
    seen=set()
    pattern_fields={'id','task_types','title','when','gates','command_illustrative','checks','implemented'}
    for pattern in patterns:
        ident=pattern.get('id')
        if set(pattern)!=pattern_fields or type(ident) is not str or not ID_RE.fullmatch(ident) or ident in seen:
            raise ValueError('Invalid or duplicate code pattern')
        seen.add(ident)
        if not _strings(pattern['task_types']) or set(pattern['task_types'])-VALID_TYPES:raise ValueError(ident+': invalid task_types')
        if pattern['implemented'] is not False:raise ValueError(ident+': illustrative pattern must have implemented=false')
        if any(type(pattern[key]) is not str or not pattern[key].strip() for key in ('title','when','gates','command_illustrative','checks')):
            raise ValueError(ident+': text fields required')
    for alias in aliases:
        if set(alias)!={'phrases','capability_ids'} or not _strings(alias['phrases']) or not _strings(alias['capability_ids']) or set(alias['capability_ids'])-ids:
            raise ValueError('Invalid alias or unknown capability reference')
    return rules,patterns,aliases

def terms(text: str) -> set[str]:return set(re.findall(r'[\w\-]+',text.casefold()))
def as_text(obj: Any) -> str:
    if obj is None:return ''
    if isinstance(obj,str):return obj
    if isinstance(obj,list):return ' '.join(as_text(item) for item in obj)
    if isinstance(obj,dict):return ' '.join(f'{key} {as_text(value)}' for key,value in obj.items())
    return str(obj)

def _aliases(query: str, rows: list[dict]) -> dict[str,list[str]]:
    matched={}
    for alias in rows:
        for phrase in alias['phrases']:
            if phrase.casefold() in query.casefold():
                for ident in alias['capability_ids']:matched.setdefault(ident,[]).append(phrase)
    return matched

def alias_matches(query: str) -> dict[str,list[str]]:
    cards=load_catalog();return _aliases(query,_asset_rows(cards)[2])
def _limit(limit: int) -> int:
    if type(limit) is not int or not 2<=limit<=6:raise ValueError('limit must be an integer from 2 to 6')
    return limit

def search_cards(cards: list[dict], query: str, limit: int = 6) -> list[tuple[float,dict,list[str]]]:
    _limit(limit)
    if type(query) is not str or not query.strip() or len(query)>2000:
        raise ValueError('query must contain 1..2000 nonblank characters')
    errors=validate_catalog(cards)
    if errors:raise ValueError('; '.join(errors))
    q=terms(query);aliases=_aliases(query,_asset_rows(cards)[2]);out=[]
    for card in cards:
        title=terms(card['title']+' '+card['id'].replace('-',' '));signals=terms(as_text(card['signals']))
        family=terms(as_text(card['task_types']))
        body=terms(as_text([card['baseline'],card['upgrade'],card['verification'],card['warning'],card['libraries']]))
        common=q&(title|signals|family|body)
        score=7*len(q&title)+5*len(q&signals)+2*len(q&family)+len(q&body)
        if query.casefold() in (card['id'].casefold(),card['title'].casefold()):score+=25
        if card['id'] in aliases:score+=40+2*max(len(text) for text in aliases[card['id']])
        if score>0:out.append((float(score),card,sorted(common|set(aliases.get(card['id'],[])))))
    return sorted(out,key=lambda row:(-row[0],row[1]['id']))[:limit]

def _facts(profile: dict) -> tuple[dict,list[str]]:
    facts=dict(profile.get('properties',{}));conflicts=[];env=profile.get('environment',{})
    for key in ('network_allowed','docker_available'):
        if key in env:
            if key in facts and facts[key]!=env[key]:
                conflicts.append(f'{key} disagrees between properties and environment')
                facts[key]=False  # Permission disagreement never selects the more permissive value.
            else:facts[key]=env[key]
    return facts,conflicts

def match_decision_rules(profile: dict, rules: list[dict] | None = None) -> list[dict]:
    errors=validate_profile(profile)
    if errors:raise ValueError('; '.join(errors))
    facts,_=_facts(profile)
    if rules is None:rules=_asset_rows(load_catalog())[0]
    return [rule for rule in rules if all(key in facts and type(facts[key]) is type(value) and facts[key]==value for key,value in rule['when'].items())]

def _lib_key(name: str) -> str:
    key=name.strip().casefold().replace('_','-')
    aliases={'ortools':'or-tools','sklearn':'scikit-learn','cv2':'opencv','pil':'pillow',
             'node':'node.js','python':'python-stdlib','python stdlib':'python-stdlib','python statistics':'python-stdlib'}
    if key in aliases:return aliases[key]
    if key.startswith('scipy.'):return 'scipy'
    if key in {'csv','json','math','pathlib','sqlite3','statistics','collections.deque','graphlib','heapq','re','unittest','timeit'}:return 'python-stdlib'
    return key

def _library_state(profile: dict, name: str) -> str:
    env=profile.get('environment',{});key=_lib_key(name)
    installed={_lib_key(value) for value in env.get('installed_libraries',[])}
    absent={_lib_key(value) for value in env.get('unavailable_libraries',[])}
    if key in absent:return 'UNAVAILABLE'
    if env.get('python_available') is False and key in {'fastapi','flask','pydantic','numpy','scipy','sympy','pandas','scikit-learn','pillow','python-stdlib'}:
        return 'UNAVAILABLE'
    if key in installed:return 'REPORTED_PRESENT_VERIFY'
    runtime_key={'python-stdlib':'python_available','node.js':'node_available'}.get(key)
    if runtime_key in env:return 'REPORTED_PRESENT_VERIFY' if env[runtime_key] else 'UNAVAILABLE'
    if env.get('library_inventory_complete') is True and key not in {'html','css','javascript','svg','markdown'}:return 'UNAVAILABLE'
    return 'UNKNOWN'

def _runtime(profile: dict,name: str) -> str:
    env=profile.get('environment',{});field=name+'_available'
    if field in env:return 'REPORTED_PRESENT_VERIFY' if env[field] else 'UNAVAILABLE'
    return _library_state(profile,'Python stdlib' if name=='python' else 'Node.js')

def _stack(profile: dict) -> tuple[str,str]:
    raw=profile.get('environment',{}).get('existing_stack','').strip();folded=raw.casefold()
    if folded in {'unknown','none','unspecified'}:return '',''
    if re.search(r'\b(node|express|next(?:\.js)?|nestjs)\b',folded):return raw,'node'
    if re.search(r'\b(python|fastapi|flask|django)\b',folded):return raw,'python'
    if re.search(r'\breact\b',folded):return raw,'react'
    return raw,'other' if raw else ''

def architecture_hint(profile: dict) -> dict:
    raw,stack=_stack(profile)
    if raw:return {'first_choice':f'Preserve existing repository stack: {raw}',
                   'fallback':'Inspect actual manifests and startup/tests before adding any runtime or service',
                   'reason':'Declared stack is not proof dependencies run; preserve tested contracts.','availability':'REQUIRES_RUNTIME_VERIFICATION'}
    kinds=set(profile.get('task_types',[]))
    if 'web_app' in kinds:
        if profile.get('properties',{}).get('requires_api_calculation') is True:
            if _runtime(profile,'node')=='REPORTED_PRESENT_VERIFY' and _runtime(profile,'python')=='UNAVAILABLE':choice='Browser UI + one Node API in the available runtime'
            elif _runtime(profile,'python')=='REPORTED_PRESENT_VERIFY':choice='Browser UI + one local Python computation/API baseline'
            else:choice='Browser UI + API contract first; backend runtime is UNKNOWN'
        else:choice='Static HTML/CSS/JavaScript baseline; add one server only if requirements need it'
    elif 'data_pipeline' in kinds:choice='Small csv/json/sqlite3 CLI in an available runtime; library upgrades require verification'
    elif kinds&{'scientific_computing','optimization','statistics_ml','computer_vision'}:choice='Small reference calculation and independent checker; prerequisites UNKNOWN until verified'
    elif 'documents_search' in kinds:choice='Literal local text search with exact source spans; check FTS5/extraction support separately'
    else:choice='Clarify outputs and actual inputs before choosing code'
    return {'first_choice':choice,'fallback':'Use existing runnable tools; do not install or scaffold automatically',
            'reason':'Smallest testable path; all runtime claims require evidence.','availability':'UNKNOWN'}

def _any_state(states: list[str]) -> str:
    if 'REPORTED_PRESENT_VERIFY' in states:return 'REPORTED_PRESENT_VERIFY'
    return 'UNAVAILABLE' if all(state=='UNAVAILABLE' for state in states) else 'UNKNOWN'

def pattern_choices(profile: dict, patterns: list[dict] | None = None) -> list[dict]:
    if patterns is None:patterns=_asset_rows(load_catalog())[1]
    requested=set(profile.get('task_types',[]));env=profile.get('environment',{});raw,stack=_stack(profile)
    fts='REPORTED_PRESENT_VERIFY' if env.get('sqlite_fts5_available') is True else 'UNAVAILABLE' if env.get('sqlite_fts5_available') is False else 'UNKNOWN'
    requirements={
        'single-py-cli':[('Python',_runtime(profile,'python'))],
        'sqlite-analysis':[('Python',_runtime(profile,'python')),('SQLite FTS5',fts)],
        'pandas-duckdb':[('Python',_runtime(profile,'python')),('pandas or DuckDB',_any_state([_library_state(profile,'pandas'),_library_state(profile,'DuckDB')]))],
        'node-vanilla':[('Node.js',_runtime(profile,'node'))],
        'python-js-vertical':[('Python',_runtime(profile,'python'))],
        'existing-react':[('Node.js',_runtime(profile,'node')),('React',_library_state(profile,'React'))],
        'graph-stdlib':[('Python',_runtime(profile,'python'))],
        'opt-greedy-check':[('Python',_runtime(profile,'python'))],
        'opt-ortools':[('Python',_runtime(profile,'python')),('OR-Tools',_library_state(profile,'OR-Tools'))],
        'scientific-scipy':[('Python',_runtime(profile,'python')),('SciPy or SymPy or NumPy',_any_state([_library_state(profile,name) for name in ['scipy','SymPy','numpy']]))],
        'vision-classical':[('Python',_runtime(profile,'python')),('OpenCV or Pillow',_any_state([_library_state(profile,'OpenCV'),_library_state(profile,'Pillow')]))],
        'statistics-holdout':[('Python',_runtime(profile,'python'))],
        'report-html':[('Python',_runtime(profile,'python'))],
        'docs-retrieval':[('Python',_runtime(profile,'python')),('SQLite FTS5',fts)]}
    candidates=[]
    for pattern in patterns:
        ident=pattern['id'];overlap=len(requested&set(pattern['task_types']))
        if not overlap:continue
        if ident=='existing-react' and 'react' not in raw.casefold():continue
        if ident=='python-js-vertical' and stack=='node':continue
        if ident=='node-vanilla' and stack in {'python','react'}:continue
        facts=profile.get('properties',{})
        if ident=='python-js-vertical' and facts.get('requires_api_calculation') is not True:continue
        if ident=='node-vanilla' and stack!='node' and facts.get('requires_api_calculation') is not True:continue
        if ident=='graph-stdlib' and facts.get('problem_structure') not in {None,'unknown','shortest_path','routing'}:continue
        if ident=='graph-stdlib' and facts.get('problem_structure')=='shortest_path' and facts.get('edge_weight_type') not in {'unweighted','nonnegative'}:continue
        if ident in {'opt-greedy-check','opt-ortools'} and facts.get('problem_structure')=='shortest_path':continue
        if ident in {'opt-greedy-check','opt-ortools'} and facts.get('decision_variable_type')=='continuous':continue
        if ident=='statistics-holdout' and facts.get('task_subtype')=='hypothesis_test':continue
        if ident=='container-optional':
            if env.get('docker_available') is not True or env.get('docker_authorized') is not True:continue
            conditions=[('Docker daemon and authorization','REPORTED_PRESENT_VERIFY')]
        elif ident=='mcp-local-optional':
            if env.get('mcp_available') is not True or profile.get('properties',{}).get('repeated_structured_invocations') is not True:continue
            conditions=[('MCP enabled','REPORTED_PRESENT_VERIFY'),('Python',_runtime(profile,'python'))]
        else:conditions=requirements.get(ident,[('Unspecified prerequisite','UNKNOWN')])
        if stack in {'node','other'} and any(name=='Python' and state!='REPORTED_PRESENT_VERIFY' for name,state in conditions):continue
        if stack=='other' and any(name=='Node.js' and state!='REPORTED_PRESENT_VERIFY' for name,state in conditions):continue
        if any(state=='UNAVAILABLE' for _,state in conditions):continue
        availability='REPORTED_PRESENT_VERIFY' if all(state=='REPORTED_PRESENT_VERIFY' for _,state in conditions) else 'UNKNOWN'
        preserve=((ident=='node-vanilla' and stack=='node') or (ident=='existing-react' and 'react' in raw.casefold())
                  or (ident=='python-js-vertical' and stack=='python'))
        score=10*overlap+(100 if availability=='REPORTED_PRESENT_VERIFY' else 0)+(200 if preserve else 0)
        candidates.append((score,{'id':ident,'title':pattern['title'],'implemented':False,
            'status':'REFERENCE_PATTERN_NOT_EXECUTABLE','availability':availability,
            'prerequisites':[{'name':name,'status':state} for name,state in conditions],
            'selection_condition':pattern['when'],'gates':pattern['gates'],'reference_file':'catalog/code_patterns.json'}))
    return [item for _,item in sorted(candidates,key=lambda row:(-row[0],row[1]['id']))[:3]]

def score_for_type(card: dict, kind: str, profile: dict, query_tokens: set[str]):
    if kind not in card['task_types'] and 'all' not in card['task_types']:return None
    score=40.0 if kind in card['task_types'] else 0.5
    why=[f'task family: {kind}'] if kind in card['task_types'] else ['cross-cutting recipe']
    hits=query_tokens&terms(as_text(card['signals']));score+=2.6*len(hits)
    if hits:why.append('signal overlap: '+', '.join(sorted(hits)[:6]))
    if card['id'] in profile.get('required_capabilities',[]):score+=80;why.append('explicit capability requested')
    if any(_library_state(profile,name)=='REPORTED_PRESENT_VERIFY' for name in card['libraries']):
        score+=3;why.append('some listed dependency reported present; not runtime-tested')
    return score,why

def _structural_issues(profile: dict, applied: list[dict]) -> tuple[list[str],dict[str,list[str]],list[str]]:
    facts,conflicts=_facts(profile);avoid={}
    for rule in applied:
        for ident in rule['avoid']:avoid.setdefault(ident,[]).append(rule['id'])
    prefer={ident for rule in applied for ident in rule['recommend']}
    for ident in prefer&set(avoid):conflicts.append(f'Conflicting rules both prefer and avoid {ident}; excluded until reviewed')
    if facts.get('has_negative_edges') is True and facts.get('edge_weight_type') in {'unweighted','nonnegative'}:
        conflicts.append('Negative edges conflict with declared unweighted/nonnegative edge type')
        for ident in ['unweighted-shortest','weighted-shortest']:avoid.setdefault(ident,[]).append('negative-edge-conflict')
    questions=[]
    if facts.get('problem_structure')=='shortest_path' and facts.get('edge_weight_type') not in {'unweighted','nonnegative','may_be_negative'}:
        for ident in ['unweighted-shortest','weighted-shortest','negative-shortest']:
            avoid.setdefault(ident,[]).append('edge-weights-not-confirmed')
        questions.append('Are edges unweighted, nonnegative weighted, or potentially negative? Choose no shortest-path algorithm until confirmed.')
    if facts.get('problem_structure')=='resource_allocation' and facts.get('decision_variable_type')=='continuous' and facts.get('linear_model_confirmed') is not True:
        avoid.setdefault('linear-programming',[]).append('linearity-not-confirmed')
        questions.append('Are objective and every constraint linear? Continuous variables alone do not justify LP.')
    if facts.get('problem_structure')=='resource_allocation':
        variable=facts.get('decision_variable_type')
        if variable=='continuous':
            for ident in ['mixed-integer','constraint-sat']:avoid.setdefault(ident,[]).append('continuous-variable-model')
        elif variable in {'integer','boolean','mixed'}:
            avoid.setdefault('continuous-opt',[]).append('integrality-required')
    if facts.get('problem_structure')=='scheduling' and facts.get('has_resource_constraints') is False and facts.get('interval_model_confirmed') is not True:
        avoid.setdefault('interval-schedule',[]).append('interval-model-not-confirmed')
        questions.append('Are jobs fixed intervals and is the intended objective compatible with interval scheduling?')
    env=profile.get('environment',{})
    raw,stack=_stack(profile)
    # These card IDs prescribe a runtime/framework; mixed-language concept cards
    # such as role-access remain eligible and list each library's own availability.
    if env.get('python_available') is False or stack=='node':
        avoid.setdefault('api-python',[]).append('python-unavailable-or-preserve-node-stack')
    if env.get('node_available') is False or stack=='python':
        avoid.setdefault('api-node',[]).append('node-unavailable-or-preserve-python-stack')
    if 'react' not in raw.casefold() or env.get('node_available') is False:
        avoid.setdefault('frontend-react',[]).append('existing-react-setup-not-confirmed')
    requested=set(profile.get('required_capabilities',[]))
    if requested&set(avoid):conflicts.append('Required capabilities excluded by structural/runtime rules: '+', '.join(sorted(requested&set(avoid))))
    if {_lib_key(x) for x in env.get('installed_libraries',[])}&{_lib_key(x) for x in env.get('unavailable_libraries',[])}:
        conflicts.append('A library is both installed and unavailable')
    for field,label in [('python_available','python-stdlib'),('node_available','node.js')]:
        if env.get(field) is False and label in {_lib_key(x) for x in env.get('installed_libraries',[])}:
            conflicts.append(field+' conflicts with installed_libraries')
    _,stack=_stack(profile)
    if stack in {'python','node'} and env.get(stack+'_available') is False:
        conflicts.append('Existing '+stack+' stack is declared unavailable; verify runtime before choosing code')
    subtype_family={'time_series_forecast':'statistics_ml','classification':'statistics_ml','regression':'statistics_ml',
        'hypothesis_test':'statistics_ml','image_comparison':'computer_vision','segmentation':'computer_vision',
        'ode':'scientific_computing','pde':'scientific_computing','policy_retrieval':'documents_search'}
    expected=subtype_family.get(facts.get('task_subtype'))
    if expected and expected not in profile.get('task_types',[]):
        conflicts.append('task_subtype requires review of missing task family: '+expected)
    return conflicts,avoid,questions

MODEL_CARDS={
    'shortest_path':{'unweighted-shortest','weighted-shortest','negative-shortest','network-graph','algorithm-selection'},
    'routing':{'traveling-salesman','vehicle-routing','local-search','algorithm-selection'},
    'assignment':{'bipartite-match','min-cost-flow','mixed-integer','constraint-sat','algorithm-selection'},
    'facility_location':{'facility-location','mixed-integer','constraint-sat','algorithm-selection'},
    'scheduling':{'resource-schedule','interval-schedule','precedence-dag','constraint-sat','mixed-integer','algorithm-selection'},
    'resource_allocation':{'linear-programming','mixed-integer','continuous-opt','constraint-sat','multiobjective','algorithm-selection'},
    'knapsack':{'knapsack','mixed-integer','algorithm-selection'},
}

def plan(profile: dict, cards: list[dict], limit: int = 6) -> dict:
    _limit(limit);errors=validate_profile(profile)+validate_catalog(cards)
    if errors:raise ValueError('; '.join(errors))
    ids={card['id'] for card in cards};required=set(profile.get('required_capabilities',[]))
    if required-ids:raise ValueError('Unknown required capability IDs: '+', '.join(sorted(required-ids)))
    rules,patterns,aliases_rows=_asset_rows(cards);kinds=list(profile.get('task_types',[]))
    base=dict(profile_id=profile.get('id','unnamed'),advisory_only=True,
        classifier='lexical heuristic; relative scores are not probabilities; applicability requires source review',
        architecture=architecture_hint(profile),unresolved=list(profile.get('unknowns',[])),
        requirements={'hard_constraints':list(profile.get('hard_constraints',[])),'deliverables':list(profile.get('deliverables',[]))},
        review_required=True,warnings=['Cards are reference recipes, not installed executable solvers.',
            'Code patterns are recommendations, not executable code or successful runtime evidence.',
            'No commands, installations, file writes, network calls or permission changes are performed.'])
    if not kinds:
        base.update(status='NEEDS_CLASSIFICATION',recommended={},validators={},decision_gates_applied=[],
            code_pattern_candidates=[],excluded_capabilities=[],conflicts=[],
            selection_summary={'limit':limit,'total_cards':0,'unique_ids':[]},
            questions=['What outputs, inputs, task families, acceptance criteria and runtime are actually specified?'])
        return base
    applied=match_decision_rules(profile,rules);conflicts,avoid,questions=_structural_issues(profile,applied)
    facts,_=_facts(profile);prefer={}
    for rule in applied:
        for index,ident in enumerate(rule['recommend']):prefer[ident]=max(prefer.get(ident,0),45-12*index)
    raw,stack=_stack(profile)
    model_allowed=MODEL_CARDS.get(facts.get('problem_structure'))
    if model_allowed:
        for card in cards:
            if card['family']=='algorithms' and card['id'] not in model_allowed and card['id'] not in prefer:
                avoid.setdefault(card['id'],[]).append('different-confirmed-problem-structure')
    if facts.get('requires_api_calculation') is True:
        if stack=='node' or (_runtime(profile,'node')=='REPORTED_PRESENT_VERIFY' and _runtime(profile,'python')=='UNAVAILABLE'):
            prefer['api-node']=max(prefer.get('api-node',0),55);avoid.setdefault('api-python',[]).append('preserve-node-backend')
        elif stack=='python':
            prefer['api-python']=max(prefer.get('api-python',0),55);avoid.setdefault('api-node',[]).append('preserve-python-backend')
        elif stack=='other':
            for ident in ['api-python','api-node']:avoid.setdefault(ident,[]).append('preserve-existing-backend')
            questions.append('Implement the API in the declared existing stack; this catalog has no verified backend pattern for it.')
        else:questions.append('Which existing/available backend runtime should serve the required API?')
    if required&set(avoid) and not any('Required capabilities' in item for item in conflicts):
        conflicts.append('Required capability conflicts with confirmed structure or preserved backend: '+', '.join(sorted(required&set(avoid))))
    query=as_text([profile.get('summary',''),profile.get('signals',[]),profile.get('deliverables',[]),profile.get('hard_constraints',[])])
    tokens,aliases=terms(query),_aliases(query,aliases_rows);rows=[]
    for kind in kinds:
        for card in cards:
            if card['id'] in avoid:continue
            scored=score_for_type(card,kind,profile,tokens)
            if scored is None:continue
            if kind not in card['task_types'] and card['id'] not in required:continue
            if (card['id'] not in required and card['id'] not in prefer and card['id'] not in aliases
                    and not tokens&terms(as_text([card['signals'],card['title']]))):continue
            score,why=scored
            if card['id'] in aliases:
                score+=30+2*max(len(text) for text in aliases[card['id']]);why.append('Korean alias: '+', '.join(aliases[card['id']][:2]))
            if card['id'] in prefer:score+=prefer[card['id']];why.append('explicit decision condition or preserved backend')
            rows.append((score,kind,card,why))
    if not rows:
        intake=next((card for card in cards if card['id']=='intake-requirements'),None)
        if intake and intake['id'] not in avoid:
            rows.append((0.5,kinds[0],intake,['Insufficient applicability evidence; classify inputs and requirements first']))
    rows.sort(key=lambda row:(-row[0],row[2]['id'],row[1]));selected,used=[],set()
    # Required cards first; then one distinct card per family; then remaining ranked cards.
    for ident in profile.get('required_capabilities',[]):
        row=next((row for row in rows if row[2]['id']==ident),None)
        if row and len(selected)<limit:selected.append(row);used.add(ident)
    for kind in kinds:
        if len(selected)>=limit:break
        if any(row[1]==kind for row in selected):continue
        row=next((row for row in rows if row[1]==kind and row[2]['id'] not in used),None)
        if row:selected.append(row);used.add(row[2]['id'])
    for row in rows:
        if len(selected)>=limit:break
        if row[2]['id'] not in used:selected.append(row);used.add(row[2]['id'])
    recommended={kind:[] for kind in kinds}
    for score,kind,card,why in selected:
        recommended[kind].append({'id':card['id'],'title':card['title'],'relative_score':round(score,1),'why':why[:3],
            'first_step':card['baseline'][:240],'caution':card['warning'][:200],
            'implementation_status':card['implementation_status'],
            'applies_to':[item for item in kinds if item in card['task_types'] or 'all' in card['task_types']],
            'candidate_libraries':[{'name':name,'status':_library_state(profile,name)} for name in card['libraries']],
            'recipe_file':'recipes/'+card['id']+'.md','details_command':'show '+card['id']})
    for kind in kinds:recommended[kind].sort(key=lambda card:(-card['relative_score'],card['id']))
    missing_required=required-used
    if missing_required and not missing_required<=set(avoid):
        conflicts.append('Required capability not selectable within family/limit: '+', '.join(sorted(missing_required-set(avoid))))
    if len(kinds)>limit:questions.append('More task families than card budget; inspect uncovered families with search/show.')
    if not any(key in facts for key in ['problem_structure','task_subtype']):
        questions.append('Structural model is UNKNOWN; lexical matches alone do not establish applicability.')
    if 'optimization' in kinds and not profile.get('objective'):questions.append('What objective, sense, units and required optimality?')
    if 'statistics_ml' in kinds and not profile.get('evaluation'):questions.append('What sampling unit, leakage-safe split and metric?')
    if 'web_app' in kinds and not profile.get('user_roles'):questions.append('What identity/role boundaries and server-side privileges?')
    if profile.get('environment',{}).get('optimality_required') is True:
        base['warnings'].append('Global optimality requires certified solver/bounds and an independently checked model; no proof supplied.')
    if facts.get('network_allowed') is False:
        base['warnings'].append('Network not allowed: no remote API/CDN/embedding or external image generation assumption.')
    if profile.get('environment',{}).get('python_available') is False:
        base['warnings'].append('Python unavailable: Python code patterns excluded; use verified existing runtime or mark NOT_RUN.')
    substantive=any(row[2]['id']!='intake-requirements' for row in selected)
    base.update(status='REVIEW_REQUIRED' if conflicts else 'DRAFT_PLAN_VERIFY_BEFORE_USE' if substantive else 'NEEDS_CLASSIFICATION',
        recommended=recommended,validators={kind:FAMILY_ROUTINES[kind] for kind in kinds},
        decision_gates_applied=[{'id':rule['id'],'why':rule['explanation'],'properties':rule['when'],
                                'prefer':rule['recommend'],'avoid':rule['avoid']} for rule in applied],
        code_pattern_candidates=pattern_choices(profile,patterns),
        excluded_capabilities=[{'id':ident,'reasons':reasons} for ident,reasons in sorted(avoid.items())],
        conflicts=conflicts,questions=questions,
        selection_summary={'limit':limit,'total_cards':len(selected),'unique_ids':[row[2]['id'] for row in selected],
            'uncovered_task_types':[kind for kind in kinds if not recommended[kind]]})
    return base

def doctor(cards: list[dict]) -> dict:
    names=['numpy','scipy','pandas','sklearn','sympy','pint','cv2','PIL','matplotlib','plotly','fastapi','pydantic','ortools','networkx','pytest'];modules={}
    for name in names:
        try:modules[name]='present (not imported/tested)' if importlib.util.find_spec(name) else 'not found'
        except (ImportError,ValueError,ModuleNotFoundError):modules[name]='not found'
    return {'python':sys.version.split()[0],'cwd':os.getcwd(),
        'tools':{key:shutil.which(key) for key in ('git','node','npm','docker','codex')},
        'modules':modules,'catalog_cards':len(cards),'network_test':'NOT_RUN','docker_daemon_test':'NOT_RUN',
        'note':'Read-only metadata check; no packages imported/installed, services started or permissions changed.'}

def _emit(value: Any) -> None:
    # ASCII-escaped JSON is UTF-8 compatible, including legacy Windows redirected streams.
    print(json.dumps(value,ensure_ascii=True,allow_nan=False,indent=2))

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(errors='backslashreplace')
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='cmd',required=True)
    item=sub.add_parser('list');item.add_argument('--family',default='');item.add_argument('--json',action='store_true')
    item=sub.add_parser('search');item.add_argument('query');item.add_argument('--limit',type=int,default=6);item.add_argument('--json',action='store_true')
    item=sub.add_parser('show');item.add_argument('id')
    item=sub.add_parser('plan');item.add_argument('profile');item.add_argument('--limit',type=int,default=6);item.add_argument('--json',action='store_true')
    sub.add_parser('doctor');sub.add_parser('verify-catalog');args=parser.parse_args(argv)
    try:
        cards=load_catalog()
        if args.cmd=='verify-catalog':
            _asset_rows(cards);_emit({'status':'PASS','card_count':len(cards),'errors':[]});return 0
        if args.cmd=='doctor':_emit(doctor(cards));return 0
        if args.cmd=='list':
            found=[card for card in cards if not args.family or card['family']==args.family]
            compact=[{key:card[key] for key in ['id','family','title','implementation_status']} for card in found]
            if args.json:_emit(compact)
            else:
                for card in compact:print(f"{card['id']:<29} [{card['family']:<14}] {card['title']}")
            return 0
        if args.cmd=='show':
            if not ID_RE.fullmatch(args.id):raise ValueError('Invalid capability ID; paths are not accepted')
            item=next((card for card in cards if card['id']==args.id),None)
            if item is None:raise ValueError('Unknown card: '+args.id)
            _emit({**item,'recipe_file':'recipes/'+item['id']+'.md','notice':'Reference recipe; verify implementation before use.'});return 0
        if args.cmd=='search':
            found=search_cards(cards,args.query,args.limit)
            if args.json:_emit([{'score':score,'id':card['id'],'title':card['title'],'family':card['family'],
                'implementation_status':card['implementation_status'],'matched':matches[:8],
                'details_command':'show '+card['id']} for score,card,matches in found])
            else:
                for score,card,matches in found:print(f"{score:5.1f} {card['id']:<28} {card['title']} [matched={','.join(matches[:6])}]")
            return 0
        result=plan(read_profile(args.profile),cards,args.limit)
        if args.json:_emit(result)
        else:
            print(f"PLAN [{result['status']}] {result['profile_id']}");print('Architecture:',result['architecture']['first_choice'])
            print('Total cards:',result['selection_summary']['total_cards'],'of',args.limit)
            for kind,items in result['recommended'].items():
                print(f'[{kind}]')
                for item in items:print(f"  {item['id']} score={item['relative_score']} :: {item['first_step']}")
            for text in result['conflicts']:print('REVIEW_REQUIRED:',text)
            for text in result['questions']:print('QUESTION:',text)
            for text in result['warnings']:print('WARNING:',text)
        return 0
    except (ValueError,OSError,UnicodeError,RecursionError) as exc:
        _emit({'status':'ERROR','error':str(exc),'actions_performed':False});return 2

if __name__=='__main__':sys.exit(main())
