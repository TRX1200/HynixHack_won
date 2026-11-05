# Role-based authorization (`role-access`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** web_app, quality_security  
**Index family:** `web`  
**Useful signals:** login, admin, employee, permissions, roles

## Suggested baseline to implement (not bundled)
Server-side identity and role checks

## Conditional upgrade to consider after a working baseline
Session expiration and unauthorized tests

## Libraries / fallback
Primary candidates: FastAPI, Flask, Express. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: preserve and verify the existing backend identity and role checks. If the server/runtime or implementation is unavailable, record NOT_RUN or BLOCKED; do not substitute a mock UI.

## Required verification
401/403 checks on protected APIs independent of UI

## Main failure mode
Two login pages, a mock role UI, or a security demonstration cannot substitute for real server-side authorization. A protected operation that accepts an unauthorized request is FAIL. An unimplemented or unexecuted check is NOT_RUN or BLOCKED, never PASS.

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
