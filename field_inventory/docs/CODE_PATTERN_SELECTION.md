# Code pattern inventory

**Do not copy illustrative commands as if files existed.** This is a choice and scaffolding specification for Codex. Each entry has `implemented: false` until tested in the target repository.

- **single-py-cli**: One Python stdlib command with testable pure functions — Small offline processing or numerical baseline; output files or JSON. Gate: No API/web server required. Test: unittest, rerun determinism, invalid schema.
- **sqlite-analysis**: SQLite normalized tables or FTS5 — Joins, provenance and local keyword search. Gate: Dataset fits in single file and local filesystem available. Test: Key/cardinality, exact document span.
- **pandas-duckdb**: Tabular analytics using pandas or DuckDB — Large joins/aggregations and exploratory metrics. Gate: Libraries installed and join grain verified. Test: Row conservation, no join multiplication.
- **node-vanilla**: Vanilla HTML/JS + Node.js HTTP — Small frontend plus simple local API. Gate: Task does not need specialized Python numerics. Test: HTTP contract plus manual UI.
- **python-js-vertical**: Python calculation/API + JS browser UI — UI needs repeated numerical or backend calculations. Gate: Both runtimes available; API schema agreed. Test: Input→HTTP→computed output + boundary errors.
- **existing-react**: Existing React/TS app, preserve installed stack — Existing project uses React or frontend complexity justifies. Gate: No unnecessary dependencies/new scaffold. Test: UI flow, type + runtime contract.
- **graph-stdlib**: Graph algorithms using Python stdlib — BFS/Dijkstra, adjacency and simple routing. Gate: Problem actually is graph model; weights verified. Test: Reachability, independent cost recomputation.
- **opt-greedy-check**: Feasible heuristic + independent verifier — Large discrete problem/time bound. Gate: Hard constraints can be checked explicitly. Test: All constraints, baseline objective, small oracle.
- **opt-ortools**: OR-Tools routing/CP-SAT/min-cost flow — Structure matches solver and package available. Gate: Time/solver-status tracked; no unapproved install. Test: Infeasible vs feasible vs OPTIMAL status + raw check.
- **scientific-scipy**: NumPy/SciPy/SymPy scientific core — ODE, linear algebra, symbolic, numeric solve. Gate: Relevant packages available. Test: Residual, limit, conservation, convergence.
- **vision-classical**: OpenCV/Pillow classical processing — Registered images, geometry or regions. Gate: Scale/ground truth documented. Test: Synthetic marks, shift negative control.
- **statistics-holdout**: Baseline and leakage-safe evaluation — Prediction/inference from labeled observations. Gate: Correct sampling unit and split. Test: Holdout, split leakage, calibration or residual.
- **report-html**: Static HTML+CSV/PNG export — Deliverable is readable report with evidence. Gate: No dynamic app necessary. Test: Numbers and source trace + visual check.
- **docs-retrieval**: Source offsets + FTS5 index — Many rules/pages searched repeatedly. Gate: Documents have extractable text or justified OCR. Test: Exact source trace, outdated clause negative.
- **container-optional**: Docker/Compose as optional wrapper — Several long-lived services/dependency reproducibility. Gate: Docker daemon available and authorized. Test: Same endpoints vs direct run.
- **mcp-local-optional**: Local stdio MCP wrapper around CLI — Repeated structured invocations benefit from tools. Gate: MCP enabled and tested; no outbound data. Test: CLI/MCP parity on fixed fixtures.
