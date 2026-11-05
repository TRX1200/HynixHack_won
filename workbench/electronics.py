"""Six small educational circuit/process calculators; Python stdlib only.

Explicit SI field names, except activation energy in eV. No network, file writes,
simulator, fitted material parameters, or process/device accuracy claim.
"""
from __future__ import annotations

import json
import math
from typing import Any

# NIST CODATA 2022 epsilon_0; k_B/e from the exact SI defining constants.
EPSILON_0_F_PER_M = 8.8541878188e-12
BOLTZMANN_EV_PER_K = 1.380649e-23 / 1.602176634e-19

FIELDS = {
    'ohm': {'voltage_v', 'resistance_ohm'},
    'rc': {'resistance_ohm', 'capacitance_f'},
    'parallel_plate': {'relative_permittivity', 'area_m2', 'thickness_m'},
    'thin_film': {'resistivity_ohm_m', 'length_m', 'width_m', 'thickness_m'},
    'arrhenius': {'activation_energy_ev', 'temperature_1_k', 'temperature_2_k'},
    'diffusion_1d': {'diffusivity_m2_per_s', 'time_s'},
}

ASSUMPTIONS = {
    'ohm': ['Ideal ohmic DC resistor with constant resistance; no self-heating model.'],
    'rc': ['Ideal first-order unloaded RC filter; no source/load impedance or parasitics.'],
    'parallel_plate': ['Uniform linear dielectric fully fills parallel plates; fringing and leakage ignored.'],
    'thin_film': ['Uniform rectangular ohmic film; constant bulk resistivity; contact and size effects ignored.'],
    'arrhenius': ['Same temperature-independent prefactor and nonnegative activation energy at both temperatures.',
                  'Ratio of Arrhenius coefficients; actual reaction-rate ratio also requires unchanged other factors.'],
    'diffusion_1d': ['Constant diffusivity, infinite homogeneous 1D medium, no drift or boundaries.',
                     'RMS displacement sqrt(2Dt), not semiconductor junction depth or a concentration profile.'],
}


def _number(value: Any, field: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f'{field}: a finite JSON number is required; strings and booleans are rejected.')
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f'{field}: number is outside supported floating-point range.') from exc
    if not math.isfinite(number):
        raise ValueError(f'{field}: NaN and infinity are rejected.')
    return number


def _positive(value: float, label: str) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{label}: nonpositive, overflowed, or underflowed result; rescale explicitly.')
    return value


def calculate(spec: dict) -> dict:
    """Calculate an explicitly selected model. Never modifies the input mapping."""
    if type(spec) is not dict or type(spec.get('calculator')) is not str or spec['calculator'] not in FIELDS:
        raise ValueError('calculator must be one of: ' + ', '.join(FIELDS))
    kind = spec['calculator']
    expected = FIELDS[kind] | {'calculator'}
    if set(spec) != expected:
        raise ValueError(f'{kind}: expected exactly these fields: {sorted(expected)}')
    values = {key: _number(spec[key], key) for key in FIELDS[kind]}
    nonnegative = {'activation_energy_ev', 'diffusivity_m2_per_s', 'time_s'}
    for key, value in values.items():
        if key == 'voltage_v':
            continue  # Voltage/current may have a direction; dissipated power stays nonnegative.
        if value < 0 or (value == 0 and key not in nonnegative):
            raise ValueError(f'{key}: must be {"nonnegative" if key in nonnegative else "strictly positive"}.')
    try:
        if kind == 'ohm':
            voltage, resistance = values['voltage_v'], values['resistance_ohm']
            current = voltage / resistance
            power = voltage * current
            if voltage != 0:
                _positive(abs(current), 'current_a'); _positive(power, 'power_w')
            results = {'current_a': current, 'power_w': power}
            formula = 'I=V/R; P=V*I'
        elif kind == 'rc':
            tau = _positive(values['resistance_ohm'] * values['capacitance_f'], 'time_constant_s')
            cutoff = _positive((1 / tau) / (2 * math.pi), 'cutoff_hz')
            results = {'time_constant_s': tau, 'cutoff_hz': cutoff}
            formula = 'tau=R*C; f_c=1/(2*pi*R*C)'
        elif kind == 'parallel_plate':
            capacitance = _positive(EPSILON_0_F_PER_M * values['relative_permittivity'] *
                                    (values['area_m2'] / values['thickness_m']), 'capacitance_f')
            results = {'capacitance_f': capacitance}
            formula = 'C=epsilon_0*epsilon_r*A/t'
        elif kind == 'thin_film':
            sheet = _positive(values['resistivity_ohm_m'] / values['thickness_m'], 'sheet_resistance_ohm_per_square')
            squares = _positive(values['length_m'] / values['width_m'], 'number_of_squares')
            resistance = _positive(sheet * squares, 'resistance_ohm')
            results = {'sheet_resistance_ohm_per_square': sheet, 'number_of_squares': squares,
                       'resistance_ohm': resistance}
            formula = 'R_sheet=rho/t; R=R_sheet*(L/W)=rho*L/(W*t)'
        elif kind == 'arrhenius':
            ea, t1, t2 = values['activation_energy_ev'], values['temperature_1_k'], values['temperature_2_k']
            exponent = (ea / BOLTZMANN_EV_PER_K) * ((t2 - t1) / t1 / t2) if ea and t1 != t2 else 0.0
            if not math.isfinite(exponent):
                raise ValueError('Arrhenius exponent exceeds floating-point range.')
            ratio = _positive(math.exp(exponent), 'rate_ratio_t2_over_t1')
            results = {'rate_ratio_t2_over_t1': ratio, 'log_rate_ratio': exponent}
            formula = 'k(T2)/k(T1)=exp[(Ea/k_B)*(1/T1-1/T2)]'
        else:
            diffusion, time = values['diffusivity_m2_per_s'], values['time_s']
            rms = math.sqrt(2) * math.sqrt(diffusion) * math.sqrt(time) if diffusion and time else 0.0
            if diffusion and time:
                _positive(rms, 'rms_displacement_m')
            results = {'rms_displacement_m': rms}
            formula = 'x_rms=sqrt(2*D*t)'
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError(f'{kind}: calculation exceeded supported floating-point range.') from exc
    if not all(math.isfinite(value) for value in results.values()):
        raise ValueError('Calculation produced a non-finite result.')
    output = {
        'calculator': kind, 'inputs': {'calculator': kind, **values}, 'results': results,
        'formula': formula, 'assumptions': list(ASSUMPTIONS[kind]),
        'model_scope': 'Educational scalar estimate; assumptions and units require task-specific review. Not SPICE, TCAD, PDK, or fabrication validation.',
        'numeric_policy': 'Binary64 approximations; finite results only; no automatic unit conversion or material lookup.',
    }
    json.dumps(output, allow_nan=False)
    return output
