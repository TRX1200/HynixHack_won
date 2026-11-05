# quality inventory — 10 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`ui-test-matrix`](../recipes/ui-test-matrix.md) | End-to-end use case coverage | Happy path + empty invalid boundary cases | Manual browser and API result agree |
| [`independent-validator`](../recipes/independent-validator.md) | Independent solution verifier | Recompute invariants from raw input/output | Fault injection; catches deliberate invalid outputs |
| [`benchmark-design`](../recipes/benchmark-design.md) | Fair baseline comparison | Same data/seed/objective/budget | Wall-clock, objective, violations, timeout flags |
| [`security-secret-scan`](../recipes/security-secret-scan.md) | Secret/data leak hygiene | Diff and allowlist review | No keys, private data or task content in public paths |
| [`runtime-diagnose`](../recipes/runtime-diagnose.md) | Environment and dependency checks | Probe commands read-only | Exact versions + import/run smoke |
| [`resilience-checkpoint`](../recipes/resilience-checkpoint.md) | Crash recovery and idempotence | Atomic state snapshot and rerun-safe commands | Repeat action does not double-write |
| [`container-choice`](../recipes/container-choice.md) | Choose Docker vs direct runtime | Direct run of one process/service | Same endpoints both modes if tested |
| [`mcp-choice`](../recipes/mcp-choice.md) | Choose MCP vs CLI utility | Simple CLI first | Same fixtures and result both interfaces |
| [`algorithm-selection`](../recipes/algorithm-selection.md) | Choose method based on problem properties | Model variables/input/output and baseline | Selection rationale and contra-indications |
| [`simulation-qa`](../recipes/simulation-qa.md) | Scientific reproducibility review | Seed, assumptions and independent analytic case | Limit cases and conservation residual |
