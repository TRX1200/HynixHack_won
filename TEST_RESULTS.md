# Actual validation — v2.1.1

2026-11-05, Windows, Python 3.12.14. No package installation.

| Check | Result | Command from repository root |
|---|---|---|
| core_full | 171 PASS / 3 skipped / 0 failures | `python -B -m unittest discover -s tests -v` |
| inventory_full | 99 PASS / 0 skipped / 0 failures | `python -B -m unittest discover -s field_inventory/tests -q` |
| ui_stdlib | 18 PASS / 0 skipped / 0 failures | `python -B -S -m unittest discover -s tests -p test_ui_router.py -v` |
| mcp_smoke | exit 0 | `python -B tools/smoke_mcp.py` |
| catalog | exit 0 | `python -B tools/inventory.py verify-catalog` |
| scope_scan | exit 0 | `python -B field_inventory/tools/public_safety_scan.py .` |

Distinct full-suite total: **270 passed, 3 skipped, zero failures** (273 discovered).
The 18-test UI stdlib run overlaps the full suite; do not count it again.
The three full-suite skips remain jsonschema/PyMuPDF absence and a Windows symlink permission limitation.
Local MCP smoke performs six checks. Catalog verification retains 90 cards.

## Approach-guide extension evidence

- This release adds generic Markdown decision guidance and links, with no new allocation solver.
- Independent read-only algorithm review found no critical error in applicability boundaries,
  solver status handling, lexicographic objectives or original-input validation guidance.
- Existing unit suites and six local MCP smoke checks were rerun; these do not execute the new prose.
- The 90 reference cards and 20 Skills remain; Python syntax, JSON and local guide links are checked.
- Previous UI-specific evidence is preserved in `docs/TEST_RESULTS_v2.1.0.md`.

## NOT_RUN / limits

Actual product screenshots, responsive layouts, UI interactions and visual quality were not tested in this
extension: the deliverable is reusable guidance and a decision CLI. A project must run its functional QA
and inspect its real rendered screens separately. Generated plans/review templates start NOT_RUN.
The existing synthetic web-demo browser evidence is historical v2.0.0 evidence, not fresh v2.1 UI QA.

The official Skill quick validator cannot run without PyYAML; the custom metadata/link/installer checks
are separate. Managed Cofa Skill discovery, MCP registration, network/preview permissions and current
event approval remain NOT_RUN. Static Python 3.10 syntax is not an actual Python 3.10 execution test.
The 90 cards and 16 algorithm/code patterns retain their advisory status. See the preserved
`docs/TEST_RESULTS_v2.0.0.md` for previous workflow scope and unimplemented scientific features.
