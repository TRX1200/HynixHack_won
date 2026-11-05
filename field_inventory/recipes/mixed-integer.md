# Mixed discrete and continuous decisions (`mixed-integer`)

**Implementation status: RECIPE_ONLY.** This card is a design/verification recipe, not bundled algorithm or application code. The inventory CLI retrieves advice; it does not implement this baseline or install its candidate libraries.

**Task families:** optimization  
**Index family:** `algorithms`  
**Useful signals:** integer, binary, budget, allocation, logical constraints

## 선택 전에 필요한 절만 읽기
문제 README를 우선하고 [알고리즘 선택 가이드](../../ALLOCATION_STRATEGY_KO.md)의 1~2절과 5절만 먼저 읽는다. 정수·연속 변수와 선형 관계, 논리·시간 제약을 구별해 MILP 또는 CP-SAT의 적합성을 확인한다. 시간 제한의 실행 가능 해를 최적해로 표시하지 않는다. 전체 가이드나 다른 카드를 한꺼번에 불러오지 않는다. 구현 뒤에는 7절로 원래 조건을 독립 검증한다.

## Suggested baseline to implement (not bundled)
Greedy feasible + verified bounds

## Conditional upgrade to consider after a working baseline
MILP/CP-SAT

## Libraries / fallback
Primary candidates: scipy.optimize, OR-Tools. Confirm the actual runtime, library availability, license and host permissions before use. Library names do not authorize installation, network calls or GUI actions.  
Fallback: Greedy repair.

## Required verification
Integrality, constraints and solver status

## Main failure mode
Time limits can return feasible non-optimal solutions

## Implementation contract to hand to Codex
1. Read task requirements, source files, schema, output contract and permissions. Determine whether this recipe truly applies; enumerate counterexamples.
2. Implement the smallest working baseline with deterministic fixtures. Avoid unrelated stack changes.
3. Build an independent test oracle or invariant checker. Inject at least one deliberate violation to ensure it fails.
4. Verify the output, run cost/time measurements where relevant, and record **PASS / FAIL / NOT RUN** with command/evidence.
5. Promote upgrades only when baseline works and there is measured need. Never claim all edge cases or optimality without proof.

## Safety boundary
Generic, public code and synthetic fixtures only. Exam problems, raw data, work logs and private notes must not enter public Git. Do not install external AI models or transmit task data.
