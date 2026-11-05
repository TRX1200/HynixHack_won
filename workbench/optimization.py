"""Small assignment examples: explicit constraints and independent validation.

Not a general optimizer. Cost = selected unit price per item; no fixed fees,
volume discounts, schedules or minimum purchases are modeled.
"""
from __future__ import annotations
import itertools
from collections import Counter
from .core import exact_decimal_add, finite_decimal
from decimal import Decimal


def normalize(spec: dict) -> tuple[list[dict], dict[str, dict]]:
    items = spec.get('items'); plans = spec.get('options')
    if not isinstance(items, list) or not items or len(items) > 50: raise ValueError('items must contain 1..50 entries.')
    if not isinstance(plans, list) or not plans or len(plans) > 100: raise ValueError('options must contain 1..100 entries.')
    if any(not isinstance(x, dict) or not isinstance(x.get('id'), str) or not x['id'] for x in items+plans):
        raise ValueError('All item and option IDs must be nonempty strings.')
    if len({x['id'] for x in items}) != len(items) or len({x['id'] for x in plans}) != len(plans):
        raise ValueError('IDs must be unique within items/options.')
    out = {}
    for p in plans:
        cost = finite_decimal(p.get('unit_cost'))
        cap = p.get('capacity', len(items))
        features = p.get('features', [])
        if cost < 0 or isinstance(cap, bool) or not isinstance(cap, int) or cap < 0: raise ValueError('Nonnegative price and integer capacity required.')
        if not isinstance(features, list) or not all(isinstance(f,str) for f in features): raise ValueError('features must be a list of strings.')
        out[p['id']] = {**p, 'cost_decimal': cost, 'capacity': cap, 'features': set(features)}
    for item in items:
        req = item.get('requires', [])
        if not isinstance(req, list) or not all(isinstance(f,str) for f in req): raise ValueError('requires must be a list of strings.')
        allowed = item.get('allowed')
        if allowed is not None and (not isinstance(allowed,list) or any(x not in out for x in allowed)):
            raise ValueError('allowed must reference declared options.')
    return items, out


def validate_assignment(spec: dict, assignment: dict) -> dict:
    items, options = normalize(spec)
    errors, use, total = [], Counter(), Decimal(0)
    expected = {i['id'] for i in items}
    if set(assignment) != expected: errors.append('Assignment must contain exactly the declared item IDs.')
    for item in items:
        name = assignment.get(item['id'])
        if not isinstance(name, str) or name not in options:
            errors.append(f"{item['id']}: unknown or missing option"); continue
        op = options[name]; use[name] += 1
        total = exact_decimal_add(total, op['cost_decimal'])
        if not set(item.get('requires', [])) <= op['features']: errors.append(f"{item['id']}: required feature missing")
        if item.get('allowed') is not None and name not in item['allowed']: errors.append(f"{item['id']}: option not allowed")
    for name, count in use.items():
        if count > options[name]['capacity']: errors.append(f'{name}: capacity exceeded')
    return {'feasible': not errors, 'errors': errors, 'recomputed_cost': str(total), 'usage': dict(use),
            'model_scope': 'Per-item unit cost + feature requirements + option capacities + allowed options only.'}


def solve_assignment(spec: dict, max_states: int = 100_000) -> dict:
    if isinstance(max_states,bool) or not 1 <= max_states <= 1_000_000: raise ValueError('max_states 1..1000000 required.')
    items, options = normalize(spec)
    max_states = min(max_states, max(1, 2_000_000 // len(items)))
    choices = []
    for i in items:
        possible = [name for name,p in options.items() if set(i.get('requires',[])) <= p['features']
                    and (i.get('allowed') is None or name in i['allowed'])]
        if not possible:
            return {'status': 'INFEASIBLE', 'reason': 'An item has no eligible option.', 'assignment': None, 'explored': 0}
        choices.append(possible)
    state_count = 1
    for ch in choices: state_count *= len(ch)
    best, best_cost, explored = None, None, 0
    for values in itertools.islice(itertools.product(*choices), max_states):
        explored += 1
        proposal = dict(zip([i['id'] for i in items], values))
        result = validate_assignment(spec, proposal)
        if result['feasible']:
            cost = finite_decimal(result['recomputed_cost'])
            if best_cost is None or cost < best_cost: best, best_cost = proposal, cost
    exhausted = explored == state_count
    status = ('OPTIMAL_ENUMERATED' if best is not None else 'INFEASIBLE') if exhausted else ('FEASIBLE_LIMIT' if best is not None else 'UNKNOWN_LIMIT')
    return {'status': status, 'assignment': best, 'cost': str(best_cost) if best_cost is not None else None,
            'explored': explored, 'effective_max_states': max_states, 'total_candidate_states': state_count, 'complete_enumeration': exhausted,
            'validation': validate_assignment(spec,best) if best else None,
            'warning': 'Optimal only for this encoded finite model, not proof that the real-world requirements were encoded correctly.'}
