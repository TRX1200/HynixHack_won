# Local persistent records (`storage-sqlite`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** web_app, data_pipeline  
**Index family:** `web`  
**Useful signals:** persistence, database, sqlite, crud

## Suggested baseline to implement (not bundled)
SQLite with parameterized queries

## Conditional upgrade to consider after a working baseline
Migrations, indices, transactions

## Libraries / fallback
Primary candidates: sqlite3, SQLAlchemy. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Append-only JSONL when tiny.

## Required verification
Reopen persistence and concurrent write tests

## Main failure mode
Concurrent writes need transaction discipline

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
