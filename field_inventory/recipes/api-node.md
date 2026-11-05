# Node computation API (`api-node`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** web_app, integration  
**Index family:** `web`  
**Useful signals:** backend, node, express, api, javascript

## Suggested baseline to implement (not bundled)
Native Node HTTP or existing Express framework

## Conditional upgrade to consider after a working baseline
Schema validation and typed route handlers

## Libraries / fallback
Primary candidates: Node.js, Express, Ajv. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Node.js HTTP.

## Required verification
Invalid payload/error path and integration tests

## Main failure mode
Do not mix runtimes without a real boundary need

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
