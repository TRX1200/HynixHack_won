#!/usr/bin/env python3
"""Six small, offline, synthetic problem archetypes with executed falsification cases.

Educational examples, not general high-performance solvers or contest validators.
Only stdlib and this toolkit's already-local workbench modules are used.
"""
from __future__ import annotations

import argparse
import copy
import csv
from datetime import date
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from workbench.core import aggregate_csv, join_audit, load_json, read_csv, write_new
from workbench.documents import extract_to_index, load_index, search_chunks
from workbench.optimization import solve_assignment

FAMILIES = ('data', 'assignment', 'timeseries', 'image', 'rc', 'documents')
EXAMPLES = ROOT / 'examples' / 'archetypes'


def put_json(path: Path, value) -> None:
    write_new(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    with path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=header, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def finite_number(value, label: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f'{label}: finite numeric value required, excluding booleans.')
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f'{label}: outside finite floating-point range.') from exc
    if not math.isfinite(result):
        raise ValueError(f'{label}: finite numeric value required.')
    return result


def close(a, b, tolerance: float = 1e-10) -> bool:
    return type(a) in (int, float) and math.isfinite(a) and math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


# DATA: production path reuses CSV helpers; oracle uses a separate csv/Fraction path.
def solve_data(left: Path, right: Path, joined: Path) -> dict:
    _, left_rows = read_csv(left)
    _, right_rows = read_csv(right)
    output = []
    for row in left_rows:
        matches = [r for r in right_rows if row['id'].strip() and r['id'].strip() and r['id'] == row['id']]
        output.extend({'id': row['id'], 'group': row['group'], 'amount': r['amount']} for r in matches)
        if not matches:
            output.append({'id': row['id'], 'group': row['group'], 'amount': ''})
    write_csv(joined, ['id', 'group', 'amount'], output)
    return {'join': join_audit(left, right, ['id']),
            'aggregate': aggregate_csv(joined, ['group'], 'amount'),
            'policy': 'Literal string IDs; SQL-like blank nonmatching keys; left join; blank amounts missing.'}


def validate_data(left: Path, right: Path, result: dict) -> list[str]:
    with left.open(encoding='utf-8', newline='') as stream:
        left_rows = list(csv.DictReader(stream))
    with right.open(encoding='utf-8', newline='') as stream:
        right_rows = list(csv.DictReader(stream))
    totals = {}
    inner = 0
    for left_row in left_rows:
        pairs = []
        for right_row in right_rows:
            if left_row['id'].strip() and right_row['id'].strip() and left_row['id'] == right_row['id']:
                pairs.append(right_row['amount'])
        inner += len(pairs)
        values = pairs if pairs else ['']
        group = totals.setdefault(left_row['group'], {'n_total': 0, 'n_valid': 0, 'n_missing': 0, 'sum': Fraction(0)})
        for value in values:
            group['n_total'] += 1
            if value.strip():
                group['n_valid'] += 1
                group['sum'] += Fraction(value)
            else:
                group['n_missing'] += 1
    errors = []
    expected_left = sum(g['n_total'] for g in totals.values())
    audit = result.get('join', {})
    if audit.get('expected_inner_rows') != inner or audit.get('expected_left_join_rows') != expected_left:
        errors.append('Join multiplicity differs from independently enumerated pairs.')
    aggregate = result.get('aggregate', {})
    if aggregate.get('source_rows') != expected_left or aggregate.get('reconciled_rows') != expected_left:
        errors.append('Aggregate row counts do not reconcile.')
    groups = aggregate.get('groups', [])
    if not isinstance(groups, list) or len(groups) != len(totals) or {g.get('group') for g in groups} != set(totals):
        return errors + ['Aggregate group identities differ.']
    for group in groups:
        expected = totals[group['group']]
        if any(group.get(k) != expected[k] for k in ('n_total', 'n_valid', 'n_missing')):
            errors.append('Group counts differ.')
        if expected['n_valid']:
            try:
                if Fraction(group.get('sum')) != expected['sum']:
                    errors.append('Exact group sum differs.')
                if abs(Fraction(group.get('mean')) - expected['sum'] / expected['n_valid']) > Fraction(1, 10**24):
                    errors.append('Group mean differs.')
            except (TypeError, ValueError, ZeroDivisionError):
                errors.append('Invalid numeric aggregate.')
        elif group.get('sum') is not None or group.get('mean') is not None:
            errors.append('All-missing group must have null sum/mean.')
    return errors


# ASSIGNMENT: existing bounded enumerator checked against a separate Fraction oracle.
def assignment_oracle(spec: dict) -> tuple[Fraction | None, list[dict]]:
    items, options = spec['items'], spec['options']
    if not 1 <= len(items) <= 7 or not 1 <= len(options) <= 6 or len(options) ** len(items) > 20_000:
        raise ValueError('Educational oracle supports at most 7 items, 6 options, and 20000 states.')
    feasible = []
    for selected in itertools.product(range(len(options)), repeat=len(items)):
        if any(sum(index == j for index in selected) > option.get('capacity', len(items))
               for j, option in enumerate(options)):
            continue
        if any(not set(item.get('requires', [])).issubset(options[j].get('features', []))
               or (item.get('allowed') is not None and options[j]['id'] not in item['allowed'])
               for item, j in zip(items, selected)):
            continue
        cost = sum((Fraction(str(options[j]['unit_cost'])) for j in selected), Fraction(0))
        feasible.append((cost, {item['id']: options[j]['id'] for item, j in zip(items, selected)}))
    if not feasible:
        return None, []
    optimum = min(cost for cost, _ in feasible)
    return optimum, [assignment for cost, assignment in feasible if cost == optimum]


def validate_small_assignment(spec: dict, result: dict) -> list[str]:
    optimum, optimal_assignments = assignment_oracle(spec)
    if optimum is None:
        return [] if result.get('status') == 'INFEASIBLE' and result.get('assignment') is None else ['False feasible/infeasible claim.']
    errors = []
    assignment = result.get('assignment')
    if result.get('status') != 'OPTIMAL_ENUMERATED' or assignment not in optimal_assignments:
        errors.append('Claimed optimum is not an independently enumerated optimal feasible assignment.')
    try:
        if Fraction(result.get('cost')) != optimum:
            errors.append('Reported cost differs from exact rational oracle.')
    except (TypeError, ValueError, ZeroDivisionError):
        errors.append('Missing or invalid cost.')
    return errors


# TIMESERIES: strictly chronological holdout; persistence is a baseline, not ML.
def forecast_persistence(spec: dict) -> dict:
    rows = spec['observations']
    cut = spec['train_count']
    if type(cut) is not int or not isinstance(rows, list) or not 1 <= cut < len(rows) <= 5000:
        raise ValueError('Need 1..4999 training rows and at least one chronological holdout row; total <=5000.')
    times = [date.fromisoformat(row['date']) for row in rows]
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError('Dates must be strictly increasing and unique; no automatic sorting.')
    values = [finite_number(row['value'], 'value') for row in rows]
    origin = rows[cut - 1]['date']
    predictions = [{'date': row['date'], 'prediction': values[cut - 1], 'based_on_through': origin} for row in rows[cut:]]
    errors = [abs(prediction['prediction'] - actual) for prediction, actual in zip(predictions, values[cut:])]
    if not all(math.isfinite(error) for error in errors):
        raise ValueError('Holdout error exceeds finite floating-point range; rescale values explicitly.')
    mae = math.fsum(error / len(predictions) for error in errors)
    return {'model': 'last-observation persistence', 'train_count': cut, 'forecast_origin': origin,
            'predictions': predictions, 'mae': mae,
            'scope': 'One fixed-origin holdout baseline. No training on holdout, fitting, tuning, confidence interval, or accuracy guarantee.'}


def validate_forecast(spec: dict, result: dict) -> list[str]:
    rows, cut = spec['observations'], spec['train_count']
    predictions = result.get('predictions', [])
    expected_origin = rows[cut - 1]['date']
    if result.get('train_count') != cut or result.get('forecast_origin') != expected_origin:
        return ['Training boundary differs from declared chronological split.']
    if not isinstance(predictions, list) or len(predictions) != len(rows) - cut:
        return ['Holdout predictions missing or duplicated.']
    baseline = Fraction(str(rows[cut - 1]['value']))
    expected_error = sum((abs(Fraction(str(row['value'])) - baseline) for row in rows[cut:]), Fraction(0)) / len(predictions)
    errors = []
    for actual, prediction in zip(rows[cut:], predictions):
        if prediction.get('date') != actual['date'] or prediction.get('based_on_through') != expected_origin:
            errors.append('Date/source mismatch or future-data leakage.')
        if not close(prediction.get('prediction'), float(baseline)):
            errors.append('Prediction differs from training-only baseline.')
    if not close(result.get('mae'), float(expected_error)):
        errors.append('MAE differs from independent holdout arithmetic.')
    return errors


# IMAGE: integer grayscale matrices, finite translation search, no Pillow/CV claim.
def matrix_shape(matrix: list) -> tuple[int, int]:
    if not isinstance(matrix, list) or not 1 <= len(matrix) <= 128 or not isinstance(matrix[0], list) or not 1 <= len(matrix[0]) <= 128:
        raise ValueError('Matrix must have 1..128 rows and columns.')
    width = len(matrix[0])
    if any(not isinstance(row, list) or len(row) != width or any(type(v) is not int or not 0 <= v <= 255 for v in row) for row in matrix):
        raise ValueError('Rectangular integer grayscale matrix in 0..255 required.')
    return width, len(matrix)


def matrix_measure(reference: list, target: list, dx: int, dy: int, threshold: int) -> dict:
    width, height = matrix_shape(reference)
    if matrix_shape(target) != (width, height):
        raise ValueError('Matrix dimensions must agree; no implicit resampling.')
    mask, differences, points = [], [], []
    for y in range(height):
        row = []
        for x in range(width):
            if 0 <= x + dx < width and 0 <= y + dy < height:
                delta = abs(reference[y][x] - target[y + dy][x + dx])
                differences.append(delta)
                row.append(int(delta >= threshold))
                if delta >= threshold:
                    points.append((x, y))
            else:
                row.append(None)
        mask.append(row)
    if not differences:
        raise ValueError('Translation has no overlap.')
    extent = [min(x for x, _ in points), min(y for _, y in points), max(x for x, _ in points) + 1, max(y for _, y in points) + 1] if points else None
    return {'dx': dx, 'dy': dy, 'overlap_pixels': len(differences), 'ignored_border_pixels': width * height - len(differences),
            'mean_absolute_difference': sum(differences) / len(differences), 'changed_pixels': len(points), 'mask': mask,
            'extent_xyxy_half_open': extent}


def compare_matrices(spec: dict) -> dict:
    reference, target = spec['reference'], spec['target']
    width, height = matrix_shape(reference)
    if matrix_shape(target) != (width, height):
        raise ValueError('Matrix sizes differ.')
    threshold, radius = spec['threshold'], spec['max_shift']
    if type(threshold) is not int or not 1 <= threshold <= 255 or type(radius) is not int or not 0 <= radius <= 4:
        raise ValueError('threshold must be integer 1..255; max_shift integer 0..4.')
    candidates = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            overlap = (width - abs(dx)) * (height - abs(dy)) if abs(dx) < width and abs(dy) < height else 0
            if overlap * 5 < width * height * 3:
                continue
            measure = matrix_measure(reference, target, dx, dy, threshold)
            candidates.append(measure)
    best = min(candidates, key=lambda m: (m['mean_absolute_difference'], -m['overlap_pixels'], abs(m['dx']) + abs(m['dy']), m['dx'], m['dy']))
    return {'unaligned': matrix_measure(reference, target, 0, 0, threshold), 'aligned': best,
            'threshold': threshold, 'candidate_count': len(candidates),
            'scope': 'Exhaustive integer translations within max_shift, >=60% overlap. No rotation, subpixel alignment, lighting correction, object detection, or defect classification.'}


def validate_matrix(spec: dict, result: dict) -> list[str]:
    reference, target = spec['reference'], spec['target']
    height, width = len(reference), len(reference[0])
    errors = []
    candidates = []
    for dy in range(-spec['max_shift'], spec['max_shift'] + 1):
        for dx in range(-spec['max_shift'], spec['max_shift'] + 1):
            coords = [(x, y) for y in range(height) for x in range(width) if 0 <= x + dx < width and 0 <= y + dy < height]
            if len(coords) * 5 < width * height * 3:
                continue
            total = sum(abs(reference[y][x] - target[y + dy][x + dx]) for x, y in coords)
            candidates.append((Fraction(total, len(coords)), -len(coords), abs(dx) + abs(dy), dx, dy))
    _, _, _, expected_dx, expected_dy = min(candidates)
    if (result.get('aligned', {}).get('dx'), result.get('aligned', {}).get('dy')) != (expected_dx, expected_dy):
        errors.append('Translation is not the independent finite-search minimum.')
    for name in ('unaligned', 'aligned'):
        measure = result.get(name, {})
        dx, dy = measure.get('dx'), measure.get('dy')
        if name == 'unaligned' and (dx, dy) != (0, 0):
            errors.append('Unaligned measurement must use zero translation.')
        if type(dx) is not int or type(dy) is not int:
            errors.append('Invalid translation coordinates.'); continue
        deltas = {(x, y): abs(reference[y][x] - target[y + dy][x + dx])
                  for y in range(height) for x in range(width) if 0 <= x + dx < width and 0 <= y + dy < height}
        if not deltas:
            errors.append('No overlapping pixels.'); continue
        changed = [xy for xy, value in deltas.items() if value >= spec['threshold']]
        expected_mask = [[int(deltas[(x, y)] >= spec['threshold']) if (x, y) in deltas else None for x in range(width)] for y in range(height)]
        extent = [min(x for x, _ in changed), min(y for _, y in changed), max(x for x, _ in changed) + 1, max(y for _, y in changed) + 1] if changed else None
        if measure.get('changed_pixels') != len(changed) or measure.get('mask') != expected_mask or measure.get('extent_xyxy_half_open') != extent:
            errors.append('Mask/count/extent differs from direct pixel comparisons.')
        if measure.get('overlap_pixels') != len(deltas) or measure.get('ignored_border_pixels') != width * height - len(deltas):
            errors.append('Overlap accounting differs.')
        if not close(measure.get('mean_absolute_difference'), sum(deltas.values()) / len(deltas)):
            errors.append('Pixel difference mean differs.')
    return errors


# RC: forward Euler discharge versus analytic closed form, with a half-step run.
def simulate_rc(spec: dict) -> dict:
    resistance = finite_number(spec['resistance_ohm'], 'resistance_ohm')
    capacitance = finite_number(spec['capacitance_f'], 'capacitance_f')
    voltage = finite_number(spec['initial_voltage_v'], 'initial_voltage_v')
    duration = finite_number(spec['duration_s'], 'duration_s')
    steps = spec['steps']
    if resistance <= 0 or capacitance <= 0 or duration < 0 or type(steps) is not int or not 1 <= steps <= 10_000:
        raise ValueError('Positive R/C, nonnegative duration, and integer steps 1..10000 required.')
    tau = resistance * capacitance
    if not math.isfinite(tau) or tau <= 0 or duration / steps > tau:
        raise ValueError('Finite positive R*C and step <= tau required for monotone Euler discharge.')
    if duration > 0 and duration / (2 * steps) == 0:
        raise ValueError('Half-step underflows floating-point range; rescale units explicitly.')
    def integrate(count):
        dt = duration / count
        value = voltage
        rows = [{'time_s': 0.0, 'voltage_v': value}]
        for number in range(1, count + 1):
            value -= value * (dt / tau)
            rows.append({'time_s': number * dt, 'voltage_v': value})
        return rows
    coarse, fine = integrate(steps), integrate(2 * steps)
    analytic = voltage * math.exp(-duration / tau)
    return {'tau_s': tau, 'coarse': coarse, 'fine': fine, 'analytic_final_v': analytic,
            'coarse_final_error_v': abs(coarse[-1]['voltage_v'] - analytic),
            'fine_final_error_v': abs(fine[-1]['voltage_v'] - analytic),
            'scope': 'Ideal unloaded constant-R/C discharge only; SI units. No source waveform, parasitics, SPICE, TCAD, or device/process validation.'}


def validate_rc(spec: dict, result: dict) -> list[str]:
    tau = spec['resistance_ohm'] * spec['capacitance_f']
    duration, initial, steps = spec['duration_s'], spec['initial_voltage_v'], spec['steps']
    analytic = initial * math.exp(-duration / tau)
    errors = []
    if not close(result.get('tau_s'), tau) or not close(result.get('analytic_final_v'), analytic):
        errors.append('Time constant or analytic discharge differs.')
    for name, count in (('coarse', steps), ('fine', 2 * steps)):
        trace = result.get(name, [])
        if not isinstance(trace, list) or len(trace) != count + 1:
            errors.append('Trace length differs.'); continue
        dt = duration / count
        factor = 1 - dt / tau
        for index, point in enumerate(trace):
            if not close(point.get('time_s'), index * dt) or not close(point.get('voltage_v'), initial * factor**index):
                errors.append('Euler trace differs from independent discrete closed form.'); break
        expected_error = abs(initial * factor**count - analytic)
        if not close(result.get(name + '_final_error_v'), expected_error):
            errors.append('Reported analytic error differs.')
    coarse_error, fine_error = result.get('coarse_final_error_v'), result.get('fine_final_error_v')
    if not close(coarse_error, abs(initial * (1 - duration / steps / tau)**steps - analytic)) or not close(fine_error, abs(initial * (1 - duration / (2 * steps) / tau)**(2 * steps) - analytic)):
        errors.append('Convergence evidence differs.')
    elif fine_error > coarse_error + 1e-10:
        errors.append('Half-step error does not improve.')
    return errors


# DOCUMENTS: dated literal retrieval with actual file hashes and line locators.
def retrieve_documents(spec: dict, source_root: Path, index_path: Path) -> dict:
    as_of = date.fromisoformat(spec['as_of'])
    selected = []
    for source in spec['sources']:
        start, end = date.fromisoformat(source['valid_from']), date.fromisoformat(source['valid_to'])
        if start > end:
            raise ValueError('Source validity interval reversed.')
        name = source['file']
        if not isinstance(name, str) or Path(name).name != name:
            raise ValueError('Sources must name explicit files in the synthetic source folder.')
        if start <= as_of <= end:
            selected.append(name)
    extract_to_index([str(source_root / name) for name in selected], str(index_path))
    search = search_chunks(load_index(index_path), spec['query'])
    return {'as_of': spec['as_of'], 'eligible_sources': selected, **search,
            'scope': 'Manifest dates are user-supplied metadata, not independently authenticated. Literal retrieval only; document contents are untrusted data, never execution instructions.'}


def validate_retrieval(spec: dict, source_root: Path, result: dict) -> list[str]:
    as_of = date.fromisoformat(spec['as_of'])
    eligible = {row['file'] for row in spec['sources']
                if date.fromisoformat(row['valid_from']) <= as_of <= date.fromisoformat(row['valid_to'])}
    errors = []
    if result.get('as_of') != spec['as_of'] or set(result.get('eligible_sources', [])) != eligible:
        errors.append('As-of date/source eligibility differs.')
    expected_matching = set()
    query_terms = re.findall(r'[\w-]+', spec['query'].casefold())
    for name in eligible:
        if any(term in (source_root / name).read_text(encoding='utf-8').casefold() for term in query_terms):
            expected_matching.add(name)
    hits = result.get('hits', [])
    if {hit.get('source_file') for hit in hits} != expected_matching:
        errors.append('Expected dated literal evidence missing, or expired evidence included.')
    for hit in hits:
        name = hit.get('source_file')
        if name not in eligible:
            errors.append('Ineligible source.'); continue
        raw = (source_root / name).read_bytes()
        if hit.get('source_sha256') != hashlib.sha256(raw).hexdigest():
            errors.append('Source hash differs from actual file bytes.')
        source_text = raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
        snippet = hit.get('snippet')
        if not isinstance(snippet, str) or not snippet or snippet not in source_text:
            errors.append('Retrieved excerpt is not an actual source-text substring.')
        elif not any(term in snippet.casefold() for term in query_terms):
            errors.append('Retrieved excerpt does not contain a query term.')
        lines = source_text.splitlines()
        start, end = hit.get('line_start'), hit.get('line_end')
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines) or hit.get('locator') != 'text':
            errors.append('Invalid source line locator.')
        elif not any(term in '\n'.join(lines[start - 1:end]).casefold() for term in query_terms):
            errors.append('Cited lines do not contain a literal query term.')
    return errors


def check_case(folder: Path, checks: list, case_id: str, polarity: str, payload: dict, errors: list[str]) -> None:
    expected_acceptance = polarity != 'negative'
    accepted = not errors
    path = folder / (case_id + '.json')
    put_json(path, {'payload': payload, 'validator_errors': errors})
    checks.append({'id': case_id, 'polarity': polarity,
                   'expected': 'ACCEPT' if expected_acceptance else 'REJECT',
                   'actual': 'ACCEPT' if accepted else 'REJECT',
                   'status': 'PASS' if accepted == expected_acceptance else 'FAIL',
                   'evidence': 'cases/' + path.name})


def run_family(family: str, output: Path) -> dict:
    fixture = load_json(EXAMPLES / (family + '.json'))
    put_json(output / 'input.json', fixture)
    cases = output / 'cases'
    cases.mkdir()
    checks = []
    if family == 'data':
        left, right = output / 'left.csv', output / 'right.csv'
        write_csv(left, ['id', 'group'], fixture['left'])
        write_csv(right, ['id', 'amount'], fixture['right'])
        result = solve_data(left, right, output / 'joined.csv')
        validate = lambda value: validate_data(left, right, value)
        bad_one = copy.deepcopy(result); bad_one['join']['expected_inner_rows'] += 1
        bad_two = copy.deepcopy(result); bad_two['aggregate']['groups'][0]['sum'] = '999'
        left_zero, right_zero = output / 'empty-left.csv', output / 'empty-right.csv'
        write_csv(left_zero, ['id', 'group'], []); write_csv(right_zero, ['id', 'amount'], [])
        boundary_input = {'left': [], 'right': []}
        boundary = solve_data(left_zero, right_zero, output / 'empty-joined.csv')
        boundary_errors = validate_data(left_zero, right_zero, boundary)
    elif family == 'assignment':
        result = solve_assignment(fixture)
        validate = lambda value: validate_small_assignment(fixture, value)
        bad_one = copy.deepcopy(result); bad_one['cost'] = '0'
        bad_two = copy.deepcopy(result); bad_two['assignment'] = {row['id']: 'basic' for row in fixture['items']}
        boundary_input = copy.deepcopy(fixture); boundary_input['items'][0]['requires'] = ['UNAVAILABLE']
        boundary = solve_assignment(boundary_input)
        boundary_errors = validate_small_assignment(boundary_input, boundary)
    elif family == 'timeseries':
        result = forecast_persistence(fixture)
        validate = lambda value: validate_forecast(fixture, value)
        bad_one = copy.deepcopy(result); bad_one['predictions'][0]['based_on_through'] = fixture['observations'][-1]['date']
        bad_two = copy.deepcopy(result)
        for row, prediction in zip(fixture['observations'][fixture['train_count']:], bad_two['predictions']):
            prediction['prediction'] = row['value']
        bad_two['mae'] = 0
        boundary_input = {'train_count': 1, 'observations': [{'date': '2026-01-01', 'value': 0}, {'date': '2026-01-02', 'value': 0}]}
        boundary = forecast_persistence(boundary_input)
        boundary_errors = validate_forecast(boundary_input, boundary)
    elif family == 'image':
        result = compare_matrices(fixture)
        validate = lambda value: validate_matrix(fixture, value)
        bad_one = copy.deepcopy(result); bad_one['unaligned']['changed_pixels'] += 1
        bad_two = copy.deepcopy(result); bad_two['aligned']['dx'] = 0; bad_two['aligned']['dy'] = 0
        boundary_input = {'reference': [[0]], 'target': [[255]], 'threshold': 255, 'max_shift': 0}
        boundary = compare_matrices(boundary_input)
        boundary_errors = validate_matrix(boundary_input, boundary)
    elif family == 'rc':
        result = simulate_rc(fixture)
        validate = lambda value: validate_rc(fixture, value)
        bad_one = copy.deepcopy(result); bad_one['coarse'][1]['voltage_v'] += 1
        bad_two = copy.deepcopy(result); bad_two['analytic_final_v'] = 999
        boundary_input = {**fixture, 'initial_voltage_v': 0}
        boundary = simulate_rc(boundary_input)
        boundary_errors = validate_rc(boundary_input, boundary)
    else:
        for source in fixture['sources']:
            name = source['file']
            write_new(output / name, (EXAMPLES / name).read_text(encoding='utf-8'))
        result = retrieve_documents(fixture, output, output / 'index.jsonl')
        validate = lambda value: validate_retrieval(fixture, output, value)
        bad_one = copy.deepcopy(result); bad_one['eligible_sources'].append('policy-2025.md')
        bad_two = copy.deepcopy(result); bad_two['hits'][0]['source_sha256'] = '0' * 64
        boundary_input = {**fixture, 'as_of': '2026-01-01'}
        boundary = retrieve_documents(boundary_input, output, output / 'boundary-index.jsonl')
        boundary_errors = validate_retrieval(boundary_input, output, boundary)
    put_json(output / 'result.json', result)
    check_case(cases, checks, 'positive-oracle', 'positive', result, validate(result))
    check_case(cases, checks, 'negative-1', 'negative', bad_one, validate(bad_one))
    check_case(cases, checks, 'negative-2', 'negative', bad_two, validate(bad_two))
    check_case(cases, checks, 'boundary', 'boundary', {'input': boundary_input, 'result': boundary}, boundary_errors)
    summary = {'family': family, 'status': 'PASS' if all(row['status'] == 'PASS' for row in checks) else 'FAIL',
               'checks': checks, 'synthetic_educational_only': True,
               'scope': 'These executed fixtures validate only this small implemented archetype. They do not validate arbitrary inventory recipes or a real task.',
               'not_run': ['Real task inputs, large-scale performance, external integrations, domain/physical validity.']}
    put_json(output / 'validation.json', summary)
    return summary


def run_demo(family: str, output: str | Path) -> dict:
    if family not in (*FAMILIES, 'all'):
        raise ValueError('Unknown family; web/API has a separate web_demo.py command.')
    destination = Path(output).expanduser()
    if destination.is_symlink() or any(parent.is_symlink() for parent in destination.parents):
        raise ValueError('Output folder must not traverse symbolic links.')
    destination.mkdir(parents=True, exist_ok=False)
    if family != 'all':
        return run_family(family, destination)
    summaries = []
    for selected in FAMILIES:
        child = destination / selected
        child.mkdir()
        summaries.append(run_family(selected, child))
    result = {'status': 'PASS' if all(row['status'] == 'PASS' for row in summaries) else 'FAIL',
              'families': summaries, 'synthetic_educational_only': True,
              'not_run': ['Web/API is a separate local web_demo.py example; no web claims are made here.']}
    put_json(destination / 'summary.json', result)
    return result


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='strict')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    demo = sub.add_parser('demo', help='Run synthetic input, solver, independent checks, two negative cases and boundary.')
    demo.add_argument('family', choices=(*FAMILIES, 'all'))
    demo.add_argument('--out', required=True, help='A NEW local folder. Existing folders are never overwritten.')
    args = parser.parse_args(argv)
    try:
        result = run_demo(args.family, args.out)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print(json.dumps({'status': result['status'], 'out': str(args.out), 'synthetic_educational_only': True}, ensure_ascii=False))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
