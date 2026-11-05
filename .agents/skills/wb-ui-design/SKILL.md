---
name: wb-ui-design
description: Choose and review UI structure for an existing app or a required new screen. Use for dashboards, admin or user workflows, visual consistency and responsive review, while preserving the current stack and separating functional evidence from actual screen checks.
---

# UI design and review

## Resources

- Kit root: `__KIT_ROOT__`
- Start index: `__KIT_ROOT__/docs/ui/README.md`
- Optional dependency-free Python router: `__KIT_ROOT__/tools/ui_router.py`
- These are original generic guidelines. Host rules and project requirements take precedence.

## Start with the task

1. Inspect the existing app, run instructions, design tokens and common components. Identify the user's main action, actual data, roles and constraints. Preserve the current stack and useful design choices. Fix the reported functional issue first.
2. Decide whether a screen is required. Do not add a dashboard to a CLI or calculation task merely for decoration. Unknown requirements remain unknown.
3. Read the start index, then only the design-system document and one relevant UX document. Add responsive guidance only when relevant. Do not load the whole UI collection by default.

## Optional routing

When Python is already available and permitted, save a local JSON profile using `primary_goal`, `ui_required`, `geo_is_primary`, `roles`, `records_volume` and optional `existing_ui` / `constraints`.
See `__KIT_ROOT__/docs/ui/DECISION_ROUTER.md` for exact values and schema examples.

```sh
python "__KIT_ROOT__/tools/ui_router.py" "path/to/profile.json" --json
```

Use the detected `python3` instead if appropriate; quote paths containing spaces. If Python is unavailable, choose documents manually. No package installation or MCP is required to read these Markdown instructions. Recommendations are heuristics, not implemented UI, security guarantees or proof of compliance.

## Apply the relevant guidance

- `DESIGN_SYSTEM.md`: reuse color, type, spacing and component patterns. A fallback token sample is optional; never overwrite an existing theme blindly.
- `DASHBOARD_UX.md`: define each real metric's meaning, period, unit, denominator, missing values and drill-down. Do not invent KPI data.
- `ADMIN_USER_UX.md`: distinguish operator workflows from ordinary user goals. Hidden buttons do not replace server authorization.
- `RESPONSIVE.md`: inspect narrow screens first; keep essential table or map scrolling local. Review 320, 390, 768 and 1440 CSS px where relevant.

Use only necessary local dependencies and permitted assets. Do not introduce external fonts, CDNs or services without a task need and authorization. Respect original licenses.

## Verify separately

After implementation, read `__KIT_ROOT__/docs/ui/VISUAL_REVIEW.md`.
Run functional checks for the actual flow, values, persistence and required server permissions. Separately inspect the rendered screen with long Korean text, empty, loading and error states, keyboard use and relevant viewport sizes.
Use real screenshots only through host-permitted tools; retain evidence locally. Generated mockups are not execution evidence.
Record functional QA and visual QA separately. Use NOT_RUN for unexecuted checks, BLOCKED for missing prerequisites, and FAIL for observed mismatches. Never turn missing runtime, screenshot or server tests into PASS.
Fix failures and repeat the same relevant check. Report the observed scope and remaining gaps; do not claim whole-product or WCAG certification.
