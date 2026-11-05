#!/usr/bin/env python3
"""Optional synthetic math/science smoke checks. No model, network, files, or installation."""
from __future__ import annotations
import json
import math

def run_checks() -> list[dict]:
    results = []
    try:
        import sympy as sp
        t, R, C = sp.symbols('t R C', positive=True)
        y = 1 - sp.exp(-t/(R*C))
        ok = sp.simplify(R*C*sp.diff(y,t) + y - 1) == 0 and y.subs(t,0) == 0
        results.append({'check':'symbolic_rc_residual_and_initial_condition','status':'pass' if ok else 'fail'})
    except ImportError:
        results.append({'check':'symbolic_rc_residual_and_initial_condition','status':'skip','reason':'sympy unavailable'})
    try:
        import numpy as np
        from scipy.integrate import solve_ivp
        from scipy import stats
        tau = 1.0  # 1000 ohm * 0.001 F, simple first-order RC example.
        t = np.linspace(0, 5, 51)
        sol = solve_ivp(lambda time,y:(1-y)/tau,(0,5),[0.],t_eval=t,rtol=1e-10,atol=1e-12)
        error = float(np.max(np.abs(sol.y[0] - (-np.expm1(-t/tau)))))
        results.append({'check':'numeric_rc_against_analytic','status':'pass' if sol.success and error < 1e-8 else 'fail','max_abs_error':error})
        a = np.array([1.,3.,4.,7.,8.]); b = np.array([3.,4.,7.,12.,14.,16.])
        actual = stats.ttest_ind(a,b,equal_var=False)
        expected_t = (a.mean()-b.mean())/np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
        results.append({'check':'welch_statistic_arithmetic','status':'pass' if math.isclose(float(actual.statistic),float(expected_t),rel_tol=1e-12) else 'fail'})
        before = np.array([2.,4.,3.,8.,7.]); after = before + np.array([1.,2.,0.,2.,1.])
        paired = stats.ttest_rel(after,before); one = stats.ttest_1samp(after-before,0.)
        results.append({'check':'paired_matches_difference_test','status':'pass' if np.allclose([paired.statistic,paired.pvalue],[one.statistic,one.pvalue],rtol=1e-12) else 'fail'})
    except ImportError:
        for name in ['numeric_rc_against_analytic','welch_statistic_arithmetic','paired_matches_difference_test']:
            results.append({'check':name,'status':'skip','reason':'numpy/scipy unavailable'})
    try:
        import pint
        u = pint.UnitRegistry()
        q = (1000*u.ohm * .001*u.farad).to(u.second)
        results.append({'check':'rc_units','status':'pass' if math.isclose(q.magnitude,1.) else 'fail'})
    except ImportError:
        results.append({'check':'rc_units','status':'skip','reason':'pint unavailable; no installation attempted'})
    return results

if __name__ == '__main__':
    try:
        checks = run_checks()
        print(json.dumps({'checks':checks,'limits':'Synthetic function checks only; do not validate arbitrary physics, study design or host compatibility.'},indent=2))
        raise SystemExit(1 if any(x['status']=='fail' for x in checks) else 0)
    except Exception as exc:
        print(json.dumps({'status':'error','type':type(exc).__name__,'message':str(exc)}))
        raise SystemExit(2)
