# Visual/interaction smoke testing (`ui-visual-qa`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** web_app, reporting  
**Index family:** `web`  
**Useful signals:** browser, css, responsive, click, form, mobile

## Suggested baseline to implement (not bundled)
Manual in-browser end-to-end walkthrough

## Conditional upgrade to consider after a working baseline
Reuse existing test code only when the host explicitly permits it; this kit does not add GUI automation

## Libraries / fallback
Primary path: manual use of the host-provided internal preview. Optional test frameworks are reference candidates only; do not install or run browser automation in a restricted environment. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Manual checklist.

## Required verification
Input→API→calculation→render on real browser

## Main failure mode
Do not use GUI automation when competition forbids it

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.

## Optional UI design route
When an actual screen is required, start at [UI guidance](../../docs/ui/README.md).
Run `python tools/ui_router.py <local-ui-profile.json> --json` from the kit root, then read
only the selected guidance. Keep the existing stack and record functional and visual checks separately.
This reference does not create a screen or prove visual quality.
