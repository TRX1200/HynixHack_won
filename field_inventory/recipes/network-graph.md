# Graph modeling primitives (`network-graph`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** optimization, geospatial  
**Index family:** `algorithms`  
**Useful signals:** nodes, edges, directed, graph, network

## Suggested baseline to implement (not bundled)
Adjacency list and explicit weights

## Conditional upgrade to consider after a working baseline
NetworkX when preinstalled

## Libraries / fallback
Primary candidates: NetworkX. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Python dict lists.

## Required verification
Reachability, duplicate node and asymmetric edges

## Main failure mode
Do not infer missing edges

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
