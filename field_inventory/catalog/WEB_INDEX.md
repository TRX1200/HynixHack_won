# web inventory — 13 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`frontend-static`](../recipes/frontend-static.md) | Minimal static interface | Vanilla JS with HTML/CSS and stable data interface | Input, visible result, error, keyboard smoke |
| [`frontend-react`](../recipes/frontend-react.md) | Component UI with state | Use existing React setup and component tree | UI flow and state transition tests |
| [`api-python`](../recipes/api-python.md) | Python computation API | Small FastAPI routes with typed data | 200/400/401/403/404/500 and schema contract |
| [`api-node`](../recipes/api-node.md) | Node computation API | Native Node HTTP or existing Express framework | Invalid payload/error path and integration tests |
| [`browser-only-calculation`](../recipes/browser-only-calculation.md) | Client-only deterministic calculator | Pure JS function + UI | Property checks and consistent results |
| [`role-access`](../recipes/role-access.md) | Role-based authorization | Server-side identity and role checks | 401/403 checks on protected APIs independent of UI |
| [`input-validation`](../recipes/input-validation.md) | Cross-language input contracts | Explicit JSON schema, reject invalid fields | Version ID unit/null/NaN/boolean tests |
| [`storage-sqlite`](../recipes/storage-sqlite.md) | Local persistent records | SQLite with parameterized queries | Reopen persistence and concurrent write tests |
| [`realtime-progress`](../recipes/realtime-progress.md) | Long operation progress | Async job ID + polling | No hanging request; cancellation and retry |
| [`ui-visual-qa`](../recipes/ui-visual-qa.md) | Visual/interaction smoke testing | Manual in-browser end-to-end walkthrough | Input→API→calculation→render on real browser |
| [`ui-map`](../recipes/ui-map.md) | Coordinate map and markers | SVG coordinate overlay on local schematic | Coordinate bounds and click-to-ID mapping |
| [`ui-chart`](../recipes/ui-chart.md) | Exploratory data chart | Plotly or static SVG with units | Axis units missing values and selection smoke |
| [`web-export`](../recipes/web-export.md) | Export consistent artifacts | JSON/CSV with deterministic naming | Export re-import roundtrip and content comparison |

## Screen design only when required
For a required visible UI, use [UI decision guidance](../../docs/ui/README.md) and the small
UI router. Preserve the six-card total limit; UI documentation is conditional reference,
not a reason to load all 90 cards or add a frontend to an API-only task.
