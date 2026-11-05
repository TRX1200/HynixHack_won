# algorithms inventory — 26 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`network-graph`](../recipes/network-graph.md) | Graph modeling primitives | Adjacency list and explicit weights | Reachability, duplicate node and asymmetric edges |
| [`unweighted-shortest`](../recipes/unweighted-shortest.md) | Unweighted shortest path | BFS | Path edge count versus exhaustive tiny graph |
| [`weighted-shortest`](../recipes/weighted-shortest.md) | Nonnegative weighted shortest path | Dijkstra | Path connectivity and independently recomputed cost |
| [`negative-shortest`](../recipes/negative-shortest.md) | Shortest paths with negative edges | Bellman-Ford with cycle detection | Negative-cycle case and finite path costs |
| [`max-flow`](../recipes/max-flow.md) | Maximum feasible flow | Edmonds-Karp on small graphs | Capacity and flow conservation |
| [`min-cost-flow`](../recipes/min-cost-flow.md) | Capacitated allocation as min-cost flow | Greedy feasible assignment | Supply/demand conservation and capacity |
| [`bipartite-match`](../recipes/bipartite-match.md) | One-to-one weighted assignment | Greedy valid pairing | One-to-one and cost oracle on small n |
| [`knapsack`](../recipes/knapsack.md) | Budget-constrained item selection | Ratio greedy as baseline | No budget excess and small exhaustive oracle |
| [`interval-schedule`](../recipes/interval-schedule.md) | Nonoverlapping interval selection | Earliest finish greedy if objective is max count | No overlaps and small exhaustive oracle |
| [`precedence-dag`](../recipes/precedence-dag.md) | Precedence and critical path | Topological sort with cycle detection | Every prerequisite precedes dependent task |
| [`resource-schedule`](../recipes/resource-schedule.md) | Resource-constrained scheduling | Feasible greedy scheduler | No overlap, time windows, capacity, precedence |
| [`traveling-salesman`](../recipes/traveling-salesman.md) | Single route visit ordering | Nearest-neighbor feasible route | Each required stop visited once; exact small n DP |
| [`vehicle-routing`](../recipes/vehicle-routing.md) | Multi-vehicle capacity and time-window routes | Feasible insertion with hard checks | All demands, vehicle loads, timing, route starts |
| [`facility-location`](../recipes/facility-location.md) | Facility or pickup point selection | Nearest open candidate assignment | Facility-open link, capacity, coverage |
| [`linear-programming`](../recipes/linear-programming.md) | Linear continuous allocation | Feasible LP specification | Primal constraints, duality gap/status if available |
| [`mixed-integer`](../recipes/mixed-integer.md) | Mixed discrete and continuous decisions | Greedy feasible + verified bounds | Integrality, constraints and solver status |
| [`constraint-sat`](../recipes/constraint-sat.md) | Combinatorial hard constraints | Backtracking on tiny case | Independent rule checker + infeasible cases |
| [`local-search`](../recipes/local-search.md) | Improve an existing discrete solution | Feasible greedy seed | Monotonic objective if improvement-only; feasibility every move |
| [`metaheuristics`](../recipes/metaheuristics.md) | Large nonconvex combinatorial search | Good baseline + repair | Seed sweeps, wall-time, feasibility, baseline |
| [`qubos`](../recipes/qubos.md) | Quadratic binary encoding | First formulate constraints directly | Recover constraints and compare to MILP baseline |
| [`continuous-opt`](../recipes/continuous-opt.md) | Constrained smooth numerical optimization | Bounded local optimizer | Original constraints, gradients, termination code |
| [`nonconvex-global`](../recipes/nonconvex-global.md) | Nonconvex or discontinuous objective | Multi-start finite-budget local | Seed stability, repeated trials and known synthetic optima |
| [`robust-optimization`](../recipes/robust-optimization.md) | Optimization under uncertain inputs | Sensitivity sweep at a named nominal case | Feasible across specified scenario set |
| [`stochastic-optimization`](../recipes/stochastic-optimization.md) | Stochastic decision problems | Monte Carlo baseline with controlled seed | Empirical violation rate and CI on holdout draws |
| [`multiobjective`](../recipes/multiobjective.md) | Multiple objectives and trade-offs | Single weighted scalar objective with explicit units | Dominance and sensitivity to scaling |
| [`fairness-metrics`](../recipes/fairness-metrics.md) | Fairness and distribution of service | Report max, quantiles and gaps | Distributional metric on original population |
