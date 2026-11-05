# Create code-rendered diagram (`synthetic-graphic`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** computer_vision, reporting  
**Index family:** `vision`  
**Useful signals:** illustration, diagram, icon, schematic, image generate

## Suggested baseline to implement (not bundled)
SVG/Pillow deterministic geometry

## Conditional upgrade to consider after a working baseline
Matplotlib charts with annotations

## Libraries / fallback
Primary candidates: SVG, Pillow, Matplotlib. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Static SVG strings.

## Required verification
Render and inspect visual output

## Main failure mode
Do not fabricate photographic evidence

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
