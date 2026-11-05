"""Small, explicit temperature data contract for a synthetic cross-language example.
Not a general schema validator, statistical model, or authorization boundary.
"""
from __future__ import annotations
import math
from typing import Any
from .core import parse_json

MAX_ROWS = 10_000

def load_json(text: str) -> Any:
    return parse_json(text)

def _keys(value: Any, expected: set[str], label: str) -> None:
    if type(value) is not dict or set(value) != expected:
        raise ValueError(f'{label}: expected exact fields {sorted(expected)}')

def _number(value: Any) -> float:
    if type(value) not in (int, float):
        raise ValueError('A finite real number is required; strings and booleans rejected.')
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError('Number out of supported range.') from exc
    if not math.isfinite(result):
        raise ValueError('Non-finite value rejected.')
    return result

def convert_temperature(payload: Any) -> dict[str, Any]:
    _keys(payload, {'schema_version', 'unit', 'items'}, 'input')
    if payload['schema_version'] != '1.0' or payload['unit'] not in ('K', 'degC'):
        raise ValueError('Unsupported schema version or temperature unit.')
    if type(payload['items']) is not list or not 1 <= len(payload['items']) <= MAX_ROWS:
        raise ValueError(f'Expected 1..{MAX_ROWS} input rows.')
    ids: set[str] = set()
    items = []
    values = []
    for row in payload['items']:
        _keys(row, {'id', 'value'}, 'row')
        ident = row['id']
        if type(ident) is not str or not ident.strip() or len(ident) > 128 or ident in ids:
            raise ValueError('Non-empty unique string ID required (max 128 characters).')
        ids.add(ident)
        converted = None
        if row['value'] is not None:
            x = _number(row['value'])
            # Explicit example-domain ceiling prevents overflow; not a physical universal bound.
            lower = 0.0 if payload['unit'] == 'K' else -273.15
            if not lower <= x <= 1_000_000:
                raise ValueError('Temperature outside this example contract range.')
            converted = x - 273.15 if payload['unit'] == 'K' else x
            values.append(converted)
        items.append({'id': ident, 'value': converted})
    result = {'schema_version': '1.0', 'unit': 'degC', 'items': items,
              'count_total': len(items), 'count_used': len(values),
              'mean': math.fsum(values) / len(values) if values else None}
    validate_result(result)
    return result

def validate_result(result: Any) -> None:
    _keys(result, {'schema_version','unit','items','count_total','count_used','mean'}, 'output')
    if result['schema_version'] != '1.0' or result['unit'] != 'degC':
        raise ValueError('Output version/unit mismatch.')
    for field in ('count_total', 'count_used'):
        if type(result[field]) is not int or not 0 <= result[field] <= MAX_ROWS:
            raise ValueError('Invalid count.')
    rows = result['items']
    if type(rows) is not list or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError('Invalid items.')
    values = []
    ids: set[str] = set()
    for row in rows:
        _keys(row, {'id','value'}, 'output row')
        ident = row['id']
        if type(ident) is not str or not ident.strip() or len(ident) > 128 or ident in ids:
            raise ValueError('Invalid output ID.')
        ids.add(ident)
        if row['value'] is not None:
            number = _number(row['value'])
            if not -273.15 <= number <= 1_000_000:
                raise ValueError('Output temperature outside contract.')
            values.append(number)
    if result['count_total'] != len(rows) or result['count_used'] != len(values):
        raise ValueError('Count does not match row contents.')
    if not values:
        if result['mean'] is not None:
            raise ValueError('Mean must be null when all values are missing.')
    else:
        mean = _number(result['mean'])
        expected = math.fsum(values) / len(values)
        if not math.isclose(mean, expected, rel_tol=1e-10, abs_tol=1e-10):
            raise ValueError('Reported mean disagrees with rows.')
