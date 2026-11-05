# AI-Readable Capability Inventory (v2.0.0)

**90 indexed capability cards** across 9 catalog families (mapped to 11 task types). The inventory is read-only advisory metadata. It is not an installed solver, a benchmark result, or a guarantee of availability.

## Fast path

Run from the main repository root (the parent of field_inventory).

```bash
python tools/inventory.py doctor
python tools/inventory.py search "time windows and fleet routing"
python tools/inventory.py list --family algorithms
python tools/inventory.py show vehicle-routing
python tools/inventory.py plan field_inventory/examples/profiles/composite_app.json
python tools/inventory.py plan field_inventory/examples/profiles/composite_app.json --json
python tools/inventory.py verify-catalog
```

Use `plan` for **decision support**, not automatic commitment. Inspect `why`, `warnings`, alternative cards, unresolved questions and package availability. Do not blindly invoke every card. Single-task selection is not equivalent to complete project architecture.

## Progressive disclosure for agents

1. Read `field_inventory/catalog/README.md` and `field_inventory/docs/PROBLEM_CLASSIFICATION.md` for scope and task families.
2. For a problem, create short `problem_profile.json` using `field_inventory/schemas/problem_profile.schema.json`.
3. Call inventory CLI plan. Read only 2–6 selected `field_inventory/recipes/*.md`.
4. Create a validation contract from `field_inventory/docs/VALIDATOR_BY_PROBLEM.md` before implementation.
5. Execute one full vertical slice; then optimize/revise.
6. Keep session state and evidence. Do not automatically install libraries or make remote calls.

## Family indexes

- [orchestration](./ORCHESTRATION_INDEX.md) — 6 cards
- [web](./WEB_INDEX.md) — 13 cards
- [data](./DATA_INDEX.md) — 10 cards
- [algorithms](./ALGORITHMS_INDEX.md) — 26 cards
- [statistics](./STATISTICS_INDEX.md) — 10 cards
- [vision](./VISION_INDEX.md) — 7 cards
- [science](./SCIENCE_INDEX.md) — 5 cards
- [report](./REPORT_INDEX.md) — 3 cards
- [quality](./QUALITY_INDEX.md) — 10 cards

## Status/limits
- `search` uses lexical token overlap, not semantic retrieval.
- `plan` is a deterministic heuristic and may pick poor candidates. It flags ambiguity and cannot infer missing constraints.
- Cards are coding choices/verification recipes, not tested implementations.
- Availability of Docker, MCP, SciPy, OpenCV, browser tools, API access and GPU must be confirmed in the actual workspace.

**Korean keyword lookup:** `field_inventory/catalog/korean_aliases.json` contains 60 curated lexical alias groups for Korean task wording. They boost retrieval only; they do **not** override actual technical applicability or structured counterindications. For example `python tools/inventory.py search '버스 노선 최적화'` or `python tools/inventory.py search '시계열 예측'`.

**Status interpretation:** all 90 recipe cards carry `implementation_status: RECIPE_ONLY`. That is deliberately different from the working `field_inventory/tools/inventory.py` search/router and `field_inventory/tools/contract_factory.py` plan generator. The selected algorithms/API libraries are *not* installed or implemented by the inventory itself.
