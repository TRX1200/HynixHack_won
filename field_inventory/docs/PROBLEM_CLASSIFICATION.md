# Problem type classification / 문제 분류

**Never assume the task is an optimization problem.** A request can be composite: document retrieval + CSV cleanup + web app + scheduling + simulation. Classify the requested *output and criterion*, not its vocabulary.

| Family (`task_types`) | Detection question | Possible modules | Mandatory independent checks |
|---|---|---|---|
| `web_app` | Must a user input/change state in browser? | HTML/JS, API, storage, RBAC | input→server→calculation→UI, invalid input, authorization |
| `data_pipeline` | Are files/tables transformed and joined? | csv/pandas/DuckDB/SQLite | raw row conservation, IDs, grain, null semantics, rerun |
| `optimization` | Choose action under objective and hard constraints? | graph, flow, greedy, MILP/CP-SAT | original constraints, objective recomputation, baseline |
| `statistics_ml` | Estimate/predict/infer from data? | statsmodels/sklearn/SciPy | leakage-safe split, uncertainty, baseline, unit of analysis |
| `computer_vision` | Extract measurements from images? | Pillow/OpenCV/skimage | coordinate, calibration, image alignment, labeled controls |
| `scientific_computing` | Solve numerical/physical equations? | SymPy/SciPy/NumPy | dimensions, residual, limit cases, convergence, BC/IC |
| `documents_search` | Find/interpret statements from documents? | FTS5/page-aware readers | exact source spans, date applicability, absent vs unknown |
| `geospatial` | Interpret physical coordinates and travel? | Haversine, supplied travel matrix, GIS | coordinates, CRS, road vs straight-line, directional travel |
| `reporting` | Produce evidence-based report, chart, export? | HTML/Matplotlib/PDF | figures, units, citations, readable export |
| `integration` | Connect components/processes/tools? | API contracts, JSON, CLI, MCP | unit/data contract, retries, no unauthorized external IO |
| `quality_security` | Debug/audit/access/restore? | unittest, diff, logs, snapshots | failed-case detection, no data leakage, save consistency |

## Three-layer task frame

1. **Problem**: decision/prediction/retrieval/transformation/simulation/recommendation/rendering. If no decision variables or objective, do not force an optimizer.
2. **Interface**: CLI/batch/web/interactive map/report/API. Output form should not dictate choice of underlying algorithm.
3. **Verification**: functional correctness, data semantics, numerical/empirical quality, security, UI usability. Each has different oracles.

## Classifying unknowns

- **KNOWN**: supported by authorized requirement/source text and source location.
- **NEEDS_CONFIRMATION**: task-critical ambiguity where authorized stakeholder can answer.
- **ASSUMED**: labeled editable parameter only if task allows approximation; test sensitivity.
- **NOT_SPECIFIED**: do not impose a hard constraint, e.g. an invented numerical upper limit.
- **BLOCKED**: required source/tool not available; implement honest fallback and flag impact.

## Stop conditions

If objective, validation method, constraints or deliverable shape are inconsistent, do not pretend to know. Ask targeted stakeholder questions when permitted. Parallel tasks can proceed only on independent, well-defined parts.
