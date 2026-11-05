"""Dependency-free utilities for audit, evidence and constraint checking.

These tools check mechanical properties; they do not establish semantic truth.
Inputs are never modified. All resource bounds fail explicitly.
"""
from __future__ import annotations

import csv
import hashlib
import heapq
import io
import itertools
import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Context, Decimal, DecimalException, Inexact, InvalidOperation, Underflow, localcontext
from pathlib import Path
from typing import Any

MAX_BYTES = 64 * 1024 * 1024
MAX_ROWS = 250_000
MAX_DECIMAL_DIGITS = 10_000
EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.codex', '.ssh', '.aws'}


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def checked_file(path: str | Path, max_bytes: int = MAX_BYTES) -> Path:
    p = Path(path).expanduser()
    if p.is_symlink():
        raise ValueError('Symbolic-link inputs are not accepted. Use a verified regular file.')
    for parent in p.parents:
        if parent.is_symlink():
            raise ValueError('Symbolic-link parent is not accepted.')
    p = p.resolve(strict=True)
    if not p.is_file():
        raise ValueError('A regular file is required.')
    if any(part in EXCLUDED or part == '.env' or part.startswith('.env.') for part in p.parts):
        raise ValueError('Credential, configuration or dependency directory is excluded.')
    if p.stat().st_size > max_bytes:
        raise ValueError(f'Input exceeds {max_bytes} bytes; partition it explicitly.')
    return p


def parse_json(text: str) -> Any:
    """Reject ambiguous objects and numbers Python cannot represent finitely."""
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def reject_constant(value: str) -> None:
        raise ValueError(f'Non-finite JSON constant is not accepted: {value}')
    def finite_float(value: str) -> float:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f'JSON number exceeds finite float range: {value}')
        if number == 0 and Decimal(value) != 0:
            raise ValueError(f'JSON number underflows finite float range: {value}')
        return number
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def load_json(path: str | Path) -> Any:
    return parse_json(checked_file(path).read_text(encoding='utf-8-sig'))


def write_new(path: str | Path, text: str) -> None:
    p = Path(path)
    # Refuse writes through symlinks and refuse replacement, even for generated files.
    if p.is_symlink() or any(x.is_symlink() for x in p.parents):
        raise ValueError('Output path must not contain symbolic links.')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
        if not text.endswith('\n'):
            f.write('\n')


def finite_decimal(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError('Boolean is not a numeric measurement.')
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError('Invalid decimal value.') from exc
    if not d.is_finite():
        raise ValueError('NaN and infinity are not allowed.')
    return d


def exact_decimal_add(left: Decimal, right: Decimal) -> Decimal:
    """Add finite Decimals exactly, or fail at an explicit digit resource bound."""
    if not left.is_finite() or not right.is_finite():
        raise ValueError('Non-finite Decimal cannot be added.')
    if any(len(value.as_tuple().digits) > MAX_DECIMAL_DIGITS for value in (left, right)):
        raise ValueError(f'Decimal coefficient exceeds {MAX_DECIMAL_DIGITS} digits.')
    if not left:
        return right
    if not right:
        return left
    exponent = min(left.as_tuple().exponent, right.as_tuple().exponent)
    digits = max(left.adjusted(), right.adjusted()) - exponent + 2
    if digits > MAX_DECIMAL_DIGITS:
        raise ValueError(f'Exact decimal sum exceeds {MAX_DECIMAL_DIGITS} aligned digits; partition or rescale explicitly.')
    try:
        with localcontext(Context(prec=max(28, digits))) as ctx:
            ctx.traps[Inexact] = True
            return left + right
    except DecimalException as exc:
        raise ValueError('Decimal sum exceeds supported arithmetic range.') from exc


def read_csv(path: str | Path, encoding: str = 'utf-8-sig', delimiter: str = ',') -> tuple[list[str], list[dict[str, str]]]:
    p = checked_file(path)
    if len(delimiter) != 1:
        raise ValueError('Delimiter must be one character.')
    with p.open(encoding=encoding, newline='') as f:
        reader = csv.reader(f, delimiter=delimiter, strict=True)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError('Empty CSV has no header.') from None
        if len(header) > 1000:
            raise ValueError('CSV has more than 1000 columns; narrow the input.')
        if not header or any(not h.strip() for h in header) or len(set(header)) != len(header):
            raise ValueError('CSV headers must be nonempty and unique. Fix explicitly; no auto-renaming.')
        rows = []
        for record_no, values in enumerate(reader, 2):
            if len(values) != len(header):
                raise ValueError(f'CSV record {record_no}: expected {len(header)} fields, got {len(values)}.')
            if len(rows) >= min(MAX_ROWS, 5_000_000 // len(header)):
                raise ValueError('CSV row limit exceeded; no partial aggregate is returned.')
            rows.append(dict(zip(header, values)))
    return header, rows


def require_columns(header: list[str], columns: list[str]) -> None:
    missing = [c for c in columns if c not in header]
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(missing))


def profile_csv(path: str | Path, key: list[str] | None = None, encoding: str = 'utf-8-sig', delimiter: str = ',') -> dict:
    header, rows = read_csv(path, encoding, delimiter)
    key = key or []
    require_columns(header, key)
    columns = {}
    for col in header:
        values = [r[col] for r in rows]
        present = [v for v in values if v.strip() != '']
        nums = []
        for v in present:
            try:
                nums.append(finite_decimal(v))
            except ValueError:
                pass
        columns[col] = {
            'missing_blank': len(values) - len(present), 'distinct_nonblank': len(set(present)),
            'finite_numeric_count': len(nums), 'non_numeric_nonblank_count': len(present) - len(nums),
            'numeric_min': str(min(nums)) if nums else None,
            'numeric_max': str(max(nums)) if nums else None,
        }
    full = Counter(tuple(r[c] for c in header) for r in rows)
    result = {'file': str(path), 'sha256': file_hash(checked_file(path)), 'rows': len(rows),
              'columns': columns, 'duplicate_full_rows_excess': sum(n - 1 for n in full.values()),
              'missing_definition': 'Only empty/whitespace values. NA/null strings are not automatically missing.',
              'limits': 'Full file within row/byte limits; no sampling; raw values are not emitted.'}
    if key:
        valid = [tuple(r[k] for k in key) for r in rows if all(r[k].strip() for k in key)]
        counts = Counter(valid)
        result['key_audit'] = {'keys': key, 'missing_key_rows': len(rows) - len(valid),
                               'duplicate_key_groups': sum(n > 1 for n in counts.values()),
                               'duplicate_key_rows_excess': sum(n - 1 for n in counts.values())}
    return result


def join_audit(left: str | Path, right: str | Path, key: list[str], encoding: str = 'utf-8-sig', delimiter: str = ',') -> dict:
    if not key:
        raise ValueError('Explicit join key is required.')
    lh, lr = read_csv(left, encoding, delimiter)
    rh, rr = read_csv(right, encoding, delimiter)
    require_columns(lh, key); require_columns(rh, key)
    def counts(rows: list[dict]) -> Counter:
        return Counter(tuple(r[k] for k in key) for r in rows if all(r[k].strip() for k in key))
    lc, rc = counts(lr), counts(rr)
    lnull, rnull = len(lr) - sum(lc.values()), len(rr) - sum(rc.values())
    inner = sum(n * rc[k] for k, n in lc.items())
    left_rows = sum(n * max(rc[k], 1) for k, n in lc.items()) + lnull
    return {'left_rows': len(lr), 'right_rows': len(rr), 'keys': key,
            'left_duplicate_key_groups': sum(v > 1 for v in lc.values()),
            'right_duplicate_key_groups': sum(v > 1 for v in rc.values()),
            'left_blank_key_rows': lnull, 'right_blank_key_rows': rnull,
            'left_unmatched_nonblank_rows': sum(v for k, v in lc.items() if k not in rc),
            'right_unmatched_nonblank_rows': sum(v for k, v in rc.items() if k not in lc),
            'many_to_many_key_groups': sum(lc[k] > 1 and rc[k] > 1 for k in lc.keys() & rc.keys()),
            'expected_inner_rows': inner, 'expected_left_join_rows': left_rows,
            'left_join_row_inflation': left_rows - len(lr),
            'null_policy': 'Blank keys do not match (SQL-like). pandas null matching can differ.',
            'key_policy': 'Exact string matching: no stripping, case folding, or leading-zero conversion.'}


def aggregate_csv(path: str | Path, groups: list[str], value: str, encoding: str = 'utf-8-sig', delimiter: str = ',') -> dict:
    header, rows = read_csv(path, encoding, delimiter)
    require_columns(header, groups + [value])
    if len(set(groups)) != len(groups):
        raise ValueError('Group columns must be unique.')
    if set(groups) & {'n_total', 'n_valid', 'n_missing', 'sum', 'mean'}:
        raise ValueError('Group column name conflicts with an aggregate output field; rename it explicitly.')
    stats: dict[tuple, dict] = {}
    for no, row in enumerate(rows, 2):
        k = tuple(row[g] for g in groups)
        item = stats.setdefault(k, {'n_total': 0, 'n_valid': 0, 'n_missing': 0, 'sum': Decimal(0)})
        item['n_total'] += 1
        if row[value].strip() == '':
            item['n_missing'] += 1
            continue
        try:
            number = finite_decimal(row[value])
        except ValueError as exc:
            raise ValueError(f'Record {no}, column {value}: invalid number. No silent drop/coercion.') from exc
        item['n_valid'] += 1
        item['sum'] = exact_decimal_add(item['sum'], number)
    records = []
    for k, st in stats.items():
        out = dict(zip(groups, k))
        out.update({n: st[n] for n in ['n_total', 'n_valid', 'n_missing']})
        out['sum'] = str(st['sum']) if st['n_valid'] else None
        try:
            with localcontext(Context(prec=28)) as ctx:
                ctx.traps[Underflow] = True
                out['mean'] = str(st['sum'] / st['n_valid']) if st['n_valid'] else None
        except DecimalException as exc:
            raise ValueError('Decimal mean exceeds supported arithmetic range.') from exc
        records.append(out)
    return {'value_column': value, 'group_columns': groups, 'source_rows': len(rows),
            'reconciled_rows': sum(r['n_total'] for r in records), 'groups': records,
            'numeric_policy': 'Exact Decimal sum (at most 10000 aligned digits); mean rounded to 28 significant digits, half-even; blank missing; invalid/nonfinite fail; empty-group sum is null.'}


def solve_order(spec: dict) -> dict:
    nodes = spec.get('nodes', [])
    edges = spec.get('before', [])
    if not isinstance(nodes, list) or not all(isinstance(n, str) and n for n in nodes) or len(set(nodes)) != len(nodes):
        raise ValueError('nodes must be unique nonempty strings.')
    if len(nodes) > 10_000 or len(edges) > 100_000:
        raise ValueError('Order problem exceeds resource limits.')
    graph = {n: set() for n in nodes}; indegree = dict.fromkeys(nodes, 0)
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2 or edge[0] not in graph or edge[1] not in graph:
            raise ValueError('Every before edge must reference two declared nodes.')
        a, b = edge
        if b not in graph[a]:
            graph[a].add(b); indegree[b] += 1
    queue = sorted(n for n in nodes if indegree[n] == 0)
    heapq.heapify(queue)
    ordered, ambiguous = [], []
    while queue:
        if len(queue) > 1 and len(ambiguous) < 20:
            ambiguous.append({'after_count': len(ordered), 'available_choices': sorted(queue)[:20]})
        n = heapq.heappop(queue); ordered.append(n)
        for nxt in sorted(graph[n]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(queue, nxt)
    cycle = len(ordered) != len(nodes)
    return {'status': 'INFEASIBLE_CYCLE' if cycle else 'FEASIBLE',
            'one_order': ordered if not cycle else None,
            'unique': False if cycle else not ambiguous,
            'ambiguity_examples': ambiguous,
            'blocked_nodes_not_exact_cycle': sorted(n for n in nodes if indegree[n] > 0) if cycle else [],
            'tie_break_note': 'Lexical ordering selects one valid solution; it is NOT a business priority.',
            'constraints_checked': len(edges)}


def validate_evidence(records: list[dict]) -> dict:
    if not isinstance(records, list) or len(records) > 10000:
        raise ValueError('Evidence must be a list with at most 10000 records.')
    errors, warnings, ids = [], [], set()
    for i, r in enumerate(records, 1):
        tag = f'record {i}'
        if not isinstance(r, dict):
            errors.append(f'{tag}: must be an object'); continue
        rid = r.get('id')
        if not isinstance(rid, str) or not rid or rid in ids:
            errors.append(f'{tag}: missing or duplicate id')
        ids.add(rid if isinstance(rid, str) else f'invalid-{i}')
        if r.get('kind') not in ['fact', 'rule', 'assumption', 'derived', 'unknown']:
            errors.append(f'{tag}: invalid kind')
        if not isinstance(r.get('statement'), str) or not r['statement'].strip():
            errors.append(f'{tag}: statement required')
        if r.get('kind') in ['fact', 'rule']:
            source = r.get('source')
            if not isinstance(source, dict) or not source.get('file') or not source.get('locator'):
                errors.append(f'{tag}: source.file and source.locator required')
            if not r.get('quote'):
                warnings.append(f'{tag}: no supporting excerpt; inspect original source')
        if r.get('kind') == 'derived' and not r.get('based_on'):
            errors.append(f'{tag}: derived claim needs based_on IDs')
        for name in ['valid_from', 'valid_to']:
            if r.get(name):
                try: date.fromisoformat(r[name])
                except (ValueError, TypeError): errors.append(f'{tag}: {name} must be an ISO date')
        if r.get('valid_from') and r.get('valid_to'):
            try:
                if date.fromisoformat(r['valid_from']) > date.fromisoformat(r['valid_to']):
                    errors.append(f'{tag}: validity interval reversed')
            except (ValueError, TypeError): pass
    for i, r in enumerate(records, 1):
        if not isinstance(r, dict): continue
        refs = r.get('based_on', [])
        if not isinstance(refs, list) or not all(isinstance(x, str) for x in refs):
            errors.append(f'record {i}: based_on must be a list of string IDs'); continue
        for ref in refs:
            if ref not in ids or ref == r.get('id'):
                errors.append(f'record {i}: unresolved or self-referencing based_on ID')
    return {'structural_valid': not errors, 'errors': errors, 'warnings': warnings,
            'semantic_truth_checked': False,
            'note': 'Valid shape does not establish truth, correct rule interpretation or absence of contradictions.'}


def inventory(root: str | Path, max_files: int = 10_000) -> dict:
    p = Path(root).resolve(strict=True)
    if not p.is_dir(): raise ValueError('Directory required.')
    items, skipped = [], []
    for base, dirs, files in os.walk(p, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not d.startswith('.') and not (Path(base)/d).is_symlink())
        for name in sorted(files):
            f = Path(base)/name
            if name.startswith('.') or f.is_symlink():
                skipped.append(str(f.relative_to(p))); continue
            if len(items) >= max_files: raise ValueError('Too many files. Narrow the input directory.')
            items.append({'path': str(f.relative_to(p)), 'suffix': f.suffix.lower(), 'bytes': f.stat().st_size})
    return {'files': items, 'count': len(items), 'skipped_hidden_or_symlink': skipped,
            'note': 'Metadata only. No file contents or credentials inspected.'}


def check_manifest(root: str | Path, spec: dict) -> dict:
    base = Path(root).resolve(strict=True)
    checks = []
    for item in spec.get('files', []):
        rel = item['path']; path = (base / rel).resolve()
        if not path.is_relative_to(base): raise ValueError('Manifest path escapes project root.')
        try:
            p = checked_file(base / rel)
            size = p.stat().st_size
            ok = size >= int(item.get('min_bytes', 1))
            notes = []
            if item.get('format') == 'json': load_json(p)
            if item.get('format') == 'csv': read_csv(p)
            if item.get('required_text'):
                text = p.read_text(encoding='utf-8')
                for t in item['required_text']:
                    if t not in text: ok = False; notes.append('Missing text: ' + t)
            checks.append({'path': rel, 'pass': ok, 'bytes': size, 'sha256': file_hash(p), 'notes': notes})
        except (ValueError, OSError, UnicodeError, csv.Error, json.JSONDecodeError) as e:
            checks.append({'path': rel, 'pass': False, 'error': str(e)})
    return {'all_passed': bool(checks) and all(c['pass'] for c in checks), 'checks': checks,
            'scope': 'File/format checks only. Semantic correctness and hidden submission rules are not checked.'}
