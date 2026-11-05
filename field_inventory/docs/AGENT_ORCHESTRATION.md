# Agents orchestration — task-adaptive

No fixed agent count. A single small task may require one Codex session. Use independent workers only through the provided, explicitly permitted agent facilities and only when files and contracts can be partitioned safely. Do not add external AI services or accounts for parallelism.

## Role options (activate on demand)

- **Dispatcher/Architect**: extracts requirements, ambiguity and risk, locks interfaces, selects recipe cards.
- **Frontend implementer**: UI and accessibility, owns only front-end files; consumes locked API schema.
- **Backend implementer**: API, core computations and authoritative server-side constraints.
- **Data engineer**: schema, cleaning, join cardinals and quality metrics.
- **Algorithm engineer**: typed objective/constraints, baseline and improvement; must not grade own result as independent evidence.
- **Independent validator**: fresh reading of raw requirements and input, isolated checker, counterexamples, property tests.
- **Recorder**: state, commands, test receipts, timestamps and unverified items. Does not modify solution.
- **Visual/UX reviewer**: manual inspection through the host-provided internal preview, functional flows and visible caveats; no GUI automation or programmatic capture in restricted environments.

## Handoff contract

`TASK_ID, requirement IDs, owner files, input/output schema, dependencies, assumptions, do-not-touch paths, runnable command, test evidence, escalation/merge conditions`.

## When not to parallelize

- Two agents edit the same files.
- API contract unresolved.
- Infrastructure is unstable and parallel agents compete for tokens/CPU.
- Problem is tiny or no independent input/output interface exists.

## In-session order

1. One dispatcher scopes questions with real stakeholder.
2. Lock minimal API contract and first useful output.
3. Split only independent work; reviewer separately constructs test data or invariants.
4. Integrate early (first functioning end-to-end case), then improve algorithms/UI.
5. Run independent checker and manual UI (if allowed).
6. Record final status and evidence, including not-tested items.
