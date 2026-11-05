# Actual validation record — v2.0.0

Date: 2026-11-05. Windows, Python 3.12.14. All results below were actually run.
Existing v1.2.0 baseline: 130 discovered, 127 passed, 3 skipped, 0 failures.
No new runtime, package, browser, external AI or server dependency was installed.

| Check | Result | Reproduction from repository root |
|---|---|---|
| `core_full` | 152 passed / 3 skipped / 0 failed | `python -B -m unittest discover -s tests -v` |
| `core_stdlib` | 144 passed / 11 skipped / 0 failed | `python -B -S -m unittest discover -s tests -q` |
| `inventory_full` | 99 passed / 0 skipped / 0 failed | `python -B -m unittest discover -s field_inventory/tests -q` |
| `inventory_stdlib` | 99 passed / 0 skipped / 0 failed | `python -B -S -m unittest discover -s field_inventory/tests -q` |
| `mcp_smoke` | exit 0 | `python -B tools/smoke_mcp.py` |
| `catalog` | exit 0 | `python -B tools/inventory.py verify-catalog` |

The full suites discover 254 unit tests: 251 passed, 3 skipped, no failures.
The separate `-S` rerun disables site packages: 243 passed, 11 skipped, no failures.
These reruns overlap; they are not 508 distinct tests. Source hashes stayed unchanged during the run.
The MCP smoke command performed six checks. The inventory catalog contains 90 valid cards.

The full run skips jsonschema and PyMuPDF because they are absent, plus a Windows symlink
permission-dependent check. The `-S` run also skips Pillow image checks. Skips are not passes.
The official Skill quick validator was attempted but did not run because PyYAML is absent.
Skill metadata, existing installer behavior, resolved inventory paths and license copying
were checked separately; this does not prove discovery inside the managed assessment IDE.

## Executed workflows

- Six synthetic archetypes: 24 executed checks — six positive, twelve deliberately corrupted
  results rejected, six boundaries. Run `python field_inventory/tools/archetypes.py demo all --out work/demo-001`
  with a new output directory. See `docs/ARCHETYPE_DEMOS.md` for precise scope.
- Actual local browser: writer form → HTTP 201 → area 6; reader write → 403;
  reader GET → 200 with the stored value. Eight HTTP test methods also check authentication,
  input validation, error handling and record behavior. No production authentication claim.
- Independent forward review: an existing Node authorization bug with Python unavailable,
  and a directed negative-edge shortest-path scenario. Reviewer used only four selected
  recipe bodies. Incorrect runtime and algorithm recommendations were reproduced, fixed,
  and rechecked on the identical profiles. This is routing evidence, not implementation
  of those two applications or proof of solver correctness.
- All 29 structural rules have positive checks; omitted facts, forbidden recommendations,
  strict profile validation and the shared six-card cap have negative checks.
- Session-state capture is non-destructive. Generated validation plans start `NOT_RUN`;
  a generated plan is never represented as an executed test.

## Explicit limits / NOT_RUN

- All 90 inventory cards are `RECIPE_ONLY`; all 16 code patterns are advisory references.
- Actual Cofa runtime, MCP registration, Skill discovery, browser preview transport,
  administrator permissions, network rules and current event approval were not tested.
- Python 3.10 grammar is statically checked; the execution environment was Python 3.12.14.
- Grouped splitting, confidence intervals, calibration, general PDE, physical image scale
  calibration, semantic contradiction detection and large-instance performance are not implemented here.
- Optional scientific package/MCP installations, real process accuracy, production auth,
  deployment and any actual assessment answer/score are not validated.

Historical supplied v1.1.0 and reviewed v1.2.0 reports remain in `docs/` and are not fresh reruns.
Machine-readable current results are in `TEST_RESULTS.json`. Publication is checked separately.
