# Validation factory by problem family / 문제별 검증기 설계

**A universal verifier is unsafe**: verification depends on what the task claims. The agent must generate a contract from actual requirements, not re-use an unrelated domain-specific checker. The table gives *families of tests*, not claimed completion.

| Family | What is true when correct? | Independent oracle | Deliberate failure case | Quality metric (if applicable) |
|---|---|---|---|---|
| Data pipeline | row/key/grain semantics preserved | original input independently re-parsed | duplicate join-key, null, empty header | row counts, missing rate |
| Web app | browser action changes intended state through backend | HTTP contract + manual UI result | wrong role, invalid input, stale state | feature coverage, latency |
| Optimization | hard constraints satisfied; objective accurately computed | distinct checker + exact tiny case or bounds | duplicate assignment, capacity/time breach | feasible rate, baseline objective, runtime, optimality gap only if bound |
| Statistics/ML | evaluation respects sampling and training boundaries | holdout/walk-forward + independent baseline | label leakage, class imbalance | MAE/PR-AUC as appropriate, CI/calibration |
| Computer vision | detected geometry matches labeled images | manually labeled masks/known markers | shift-only image, scale change, false contrast | IoU/precision/measurement error |
| Scientific/physical | equations, units, BC/IC respected | analytic/manufactured solution and residual | wrong unit, sign, unstable dt | residual norm, convergence order |
| Document retrieval | every quoted claim traceable | page/line-aware source view | similar but expired clause, missing text | citation precision and relevant recall |
| Geospatial | coordinates and routes correspond to correct model | known coordinate pairs, provided matrix | swapped lat/lon, crossing obstacle | spatial distance error and service coverage |
| Visualization | chart faithfully reflects source data | independent aggregation table | truncated axis, missing nulls, swapped units | label/axis/accessibility checks |
| Integration/runtime | components communicate safely and reproducibly | cross-boundary tests, local replay | unavailable service, duplicate retries | success rate, exact versions |
| Security/auth | unauthorized request cannot perform privileged action | unauthenticated/foreign-role HTTP requests | UI-hidden but API-open mutation | 401/403 coverage |
| Report/export | same data appears in report and source | recalculate figure/table numbers | unsupported claim, broken font | complete claims/traces |

## Generate a `VALIDATION_CONTRACT.md` per new task

Each test records: requirement ID, raw source evidence, property, independently derived expected behavior, positive fixture, negative fixture, exact command, input scope, status (`PASS/FAIL/NOT_RUN/NA`), and trace (log path). Unknown specification → `NOT_RUN` or `BLOCKED`, not PASS.

## Optimization-specific additions

- **Feasibility vs quality vs proven optimality**: all distinct. A valid Greedy+2-opt route is not guaranteed globally optimal.
- Compare baseline and candidate with identical inputs, hard constraints and cost units, wall-time limits, environment, and seed; compute objective from raw route/assignment rather than trusting solver's reported value.
- For directed travel-time matrices, reversing a segment changes arc costs; evaluate actual directed edges.
- For tiny test cases, solve exactly with exhaustive search/DP or a certified solver within a strict size cap; large cases need bounds or honest `FEASIBLE_UNPROVEN`.

## Statistical-specific additions

- Preserve original sample unit; repeated measurements are not independent subjects.
- Do not fit preprocessors or feature selectors on held-out data.
- Use temporal or grouped split when records share time/person/device.
- Cite measured outcomes and uncertainty; no claims from invented labels.

## UI-specific additions

- Two login screens are **not** authorization: assert unauthorized API operations return 401/403.
- Confirm true Browser interaction manually when automated GUI actions are prohibited.
- Ensure errors are visible and recoverable, and running server remains alive.

## Fault injection protocol

1. Prepare one verified passing fixture and at least 2 deliberately failing fixtures per task family.
2. Run checker against all; require checker failure on each intended fault.
3. Mutate one relevant boundary (null, duplicate, out-of-range, unauthorized, direction swap, label leak) and rerun.
4. Log commands and counts. A LLM-written PASS statement without trace is `NOT_RUN`.
