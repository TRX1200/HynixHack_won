# orchestration inventory — 6 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`intake-requirements`](../recipes/intake-requirements.md) | Requirements and unknowns extraction | Facts/Unknowns/Assumptions/Out of scope matrix | Every requirement has provenance and acceptance criterion |
| [`stakeholder-questions`](../recipes/stakeholder-questions.md) | Stakeholder question prioritizer | Blocker vs nonblocker questions, grouped by decision impact | Each answered question changes explicit requirement or is marked no-impact |
| [`agent-boundaries`](../recipes/agent-boundaries.md) | Agent task partition and handoff | Owner files and stable contracts before parallel work | No overlapping writes, interface integration test |
| [`repo-audit`](../recipes/repo-audit.md) | Existing repository audit | Read repo layout, docs, tests, locked dependencies | Baseline tests saved and diffs reviewed |
| [`progress-checkpoint`](../recipes/progress-checkpoint.md) | Resumable session state | TASK_STATE and evidence log | Cold-read resume test from state only |
| [`feasible-scope`](../recipes/feasible-scope.md) | Time-budgeted delivery sizing | Minimum vertical slice plus smoke test | Core use case demonstrable before polish |
