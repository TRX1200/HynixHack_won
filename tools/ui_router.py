#!/usr/bin/env python3
"""Small offline UI decision aid. Explicit facts only; no code/UI generation or writes."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
MAX_PROFILE_BYTES=65536
GOALS={'analyze','manage','submit','locate','explore','present','unknown'}
PATTERNS={'analyze':'dashboard','manage':'admin-workspace','submit':'input-form',
          'explore':'search-detail','present':'presentation'}
COMMON_DOCS=['docs/ui/README.md','docs/ui/DESIGN_SYSTEM.md']
DOCS={
    'dashboard':['docs/ui/DASHBOARD_UX.md'],
    'admin-workspace':['docs/ui/ADMIN_USER_UX.md'],
    'input-form':['docs/ui/ADMIN_USER_UX.md'],
    'map-explorer':['docs/ui/RESPONSIVE.md'],
    'search-detail':['docs/ui/RESPONSIVE.md'],
    'presentation':['docs/ui/RESPONSIVE.md'],
}


def validate_profile(value: Any) -> list[str]:
    if type(value) is not dict:return ['profile must be an object']
    required={'primary_goal','ui_required','geo_is_primary','roles','records_volume'}
    allowed=required|{'id','existing_ui','constraints'}
    errors=[]
    if set(value)-allowed:errors.append('Unknown fields: '+', '.join(str(k) for k in set(value)-allowed))
    if required-set(value):errors.append('Missing fields: '+', '.join(sorted(required-set(value))))
    for key in ['primary_goal','records_volume']:
        options=GOALS if key=='primary_goal' else {'small','large','unknown'}
        if type(value.get(key)) is not str or value[key] not in options:errors.append(key+': unsupported enum value')
    for key in ['ui_required','geo_is_primary']:
        if key in value and value[key] is not None and type(value[key]) is not bool:
            errors.append(key+': expected boolean or null; numeric booleans are rejected')
    for key in ['roles','constraints']:
        if key not in value and key=='constraints':continue
        items=value.get(key)
        if (type(items) is not list or len(items)>(32 if key=='roles' else 128)
                or any(type(item) is not str or not item.strip() or len(item)>2048 for item in items)):
            errors.append(key+': expected a bounded list of nonblank strings')
        elif len(items)!=len(set(items)):errors.append(key+': duplicate values')
    for key in ['id','existing_ui']:
        if key in value and (type(value[key]) is not str or len(value[key])>2048):
            errors.append(key+': expected a string of at most 2048 characters')
    return errors


def read_profile(path: str | Path) -> dict:
    source=Path(path).expanduser()
    if source.is_symlink() or any(parent.is_symlink() for parent in source.parents):
        raise ValueError('Symbolic-link profile paths are not accepted')
    source=source.resolve(strict=True)
    if not source.is_file() or source.stat().st_size>MAX_PROFILE_BYTES:
        raise ValueError('Profile must be a regular UTF-8 JSON file of at most 65536 bytes')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate JSON key: '+key)
            result[key]=value
        return result
    def constant(value):raise ValueError('Non-finite JSON constant: '+value)
    def number(value):
        result=float(value)
        if not math.isfinite(result):raise ValueError('JSON numeric overflow')
        return result
    try:
        value=json.loads(source.read_text(encoding='utf-8-sig'),object_pairs_hook=unique,
                         parse_constant=constant,parse_float=number)
    except RecursionError as exc:raise ValueError('Profile nesting exceeds supported limit') from exc
    errors=validate_profile(value)
    if errors:raise ValueError('; '.join(errors))
    return value


def route(profile: dict) -> dict:
    """Return an advisory layout decision without reading task text semantically."""
    errors=validate_profile(profile)
    if errors:raise ValueError('; '.join(errors))
    goal=profile['primary_goal'];required=profile['ui_required'];geo=profile['geo_is_primary']
    conflicts=[];questions=[];evidence=[];pattern=None
    if required is not False and goal=='locate' and geo is False:
        conflicts.append('locate conflicts with geo_is_primary=false; clarify whether locating means spatial navigation or text search')
    if required is not False and geo is True and goal in {'manage','submit','present'}:
        conflicts.append('Primary geography and primary operation/presentation compete; clarify the main workflow before choosing a composite layout')
    if required is False:
        pattern='none';evidence.append('ui_required=false explicitly selects a CLI/file/report workflow without building a UI')
    elif required is None:
        questions.append('Is a UI an actual required deliverable?')
    elif goal=='unknown':
        questions.append('Which primary user outcome is required? Keywords and role names are insufficient.')
    elif goal=='locate':
        if geo is True:
            pattern='map-explorer';evidence.append('primary_goal=locate and geo_is_primary=true')
        elif geo is None:questions.append('Is spatial position/navigation confirmed as the primary need?')
    elif goal in {'analyze','explore'} and geo is True:
        pattern='map-explorer';evidence.append('Explicit geographic priority with analysis/exploration goal')
    else:
        pattern=PATTERNS.get(goal)
        if pattern:evidence.append('Explicit primary_goal='+goal+'; role names and keywords did not select the layout')
    if required is True and geo is None and goal!='locate':
        questions.append('Geographic priority is unknown; retain the goal-based small baseline and confirm before adding a map.')
    if required is True and profile['records_volume']=='unknown':
        questions.append('Record volume is unknown; confirm pagination/filtering needs with representative data. This does not block the primary workflow.')
    if conflicts:pattern=None
    existing=profile.get('existing_ui','').strip()
    if existing and pattern not in (None,'none'):
        questions.append('Inspect the existing UI before applying the proposed pattern; refine current components and routes, do not replace the layout automatically.')
    status='REVIEW_REQUIRED' if conflicts or (existing and pattern not in (None,'none')) else 'NEEDS_CLASSIFICATION' if pattern is None else 'DRAFT_UI_PLAN'
    documents=[] if pattern=='none' else COMMON_DOCS+(
        ['docs/ui/DECISION_ROUTER.md']+DOCS.get(pattern,[]) if status=='REVIEW_REQUIRED'
        else DOCS.get(pattern,['docs/ui/DECISION_ROUTER.md']))
    review_documents=[] if pattern=='none' else ['docs/ui/VISUAL_REVIEW.md']
    cards=[]
    if pattern not in (None,'none'):
        if pattern=='map-explorer':cards.append('ui-map')
        elif pattern=='dashboard':cards.append('ui-chart')
        elif pattern=='presentation':cards.append('ui-visual-qa')
        else:cards.append('input-validation')
        cards.append('ui-test-matrix')
        if profile['roles'] or pattern=='admin-workspace':cards.append('role-access')
    if profile['records_volume']=='large' and pattern not in (None,'none'):
        questions.append('Verify search/filtering, bounded pagination and an empty/error state with representative record counts; volume alone does not choose an admin layout.')
    if pattern=='map-explorer':
        questions.append('Confirm CRS, coordinate order, supplied data and distance semantics; map tiles/geocoding/providers are not assumed.')
    return {
        'profile_id':profile.get('id','unnamed'),'status':status,'advisory_only':True,
        'recommended_pattern':pattern,'evidence':evidence,'conflicts':conflicts,'questions':questions,
        'documents':documents[:4],'review_documents':review_documents,
        'document_phases':{'documents':'initial_design','review_documents':'after_a_usable_ui_exists'},
        'inventory_cards':cards[:3],
        'existing_ui_policy':{'preserve_existing':bool(existing),'description':existing or None,
                              'replacement_authorized':False},
        'fallback':'For location workflows use supplied coordinates with a table/list and search when a map cannot be supported; otherwise use a small list/form or CLI/file output matching the requirement.',
        'authorization_note':'Admin/user labels and separate pages do not enforce authorization. Protected actions require actual server-side identity/permission checks and positive/negative tests.',
        'external_network_required':False,'api_key_required':False,
        'scope':'Reference decision only; no files, layout, packages, services, network permissions or authentication are changed. No third-party skill content is embedded.',
    }


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile',help='Explicit local JSON UI profile')
    parser.add_argument('--json',action='store_true',help='Emit structured decision JSON')
    args=parser.parse_args(argv)
    try:result=route(read_profile(args.profile))
    except (ValueError,OSError,UnicodeError) as exc:
        print(json.dumps({'status':'ERROR','error':str(exc)},ensure_ascii=True,allow_nan=False));return 2
    if args.json:print(json.dumps(result,ensure_ascii=True,allow_nan=False,indent=2))
    else:
        print('UI decision:',result['status'],result['recommended_pattern'] or 'unresolved')
        for path in result['documents']:print('READ:',path)
        for question in result['questions']:print('QUESTION:',question.encode('ascii','backslashreplace').decode('ascii'))
        for conflict in result['conflicts']:print('REVIEW:',conflict)
        print('Permission checks remain server-side; this tool performs no actions.')
    return 0


if __name__=='__main__':raise SystemExit(main())
