# Cross-language input contracts (`input-validation`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** web_app, integration, data_pipeline  
**Index family:** `web`  
**Useful signals:** api contract, json, schema, null, ids, units

## Suggested baseline to implement (not bundled)
Explicit JSON schema, reject invalid fields

## Conditional upgrade to consider after a working baseline
Runtime validators and contract tests

## Libraries / fallback
Primary candidates: Pydantic, Ajv, jsonschema. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Hand-written stdlib validation.

## Required verification
Version ID unit/null/NaN/boolean tests

## Main failure mode
TypeScript types do not validate runtime JSON

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
