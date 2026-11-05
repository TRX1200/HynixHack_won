# Structured model-choice decision gates

Use `properties` in the profile only for facts confirmed from source, not guesses. If a property is unknown, do not trigger a branch.

- **graph-unweighted** when `{"problem_structure": "shortest_path", "edge_weight_type": "unweighted"}` → prefer `unweighted-shortest`, avoid `weighted-shortest, negative-shortest`. Use BFS for equal edge cost, test reachability
- **graph-nonnegative** when `{"problem_structure": "shortest_path", "edge_weight_type": "nonnegative"}` → prefer `weighted-shortest`, avoid `negative-shortest`. Dijkstra requires nonnegative edge weights
- **graph-negative** when `{"problem_structure": "shortest_path", "edge_weight_type": "may_be_negative"}` → prefer `negative-shortest`, avoid `weighted-shortest`. Bellman-Ford and negative-cycle detection
- **assignment-one-to-one** when `{"problem_structure": "assignment", "capacity_model": "one_to_one"}` → prefer `bipartite-match`, avoid `min-cost-flow`. Verify every item matched at most once
- **assignment-many-to-one** when `{"problem_structure": "assignment", "capacity_model": "many_to_one"}` → prefer `min-cost-flow`, avoid `bipartite-match`. Use capacity-preserving flow/MILP; one-to-one matching may be invalid
- **assignment-facilities** when `{"problem_structure": "facility_location"}` → prefer `facility-location`, avoid `(none)`. Facility opening and assignment are linked decisions
- **routing-single** when `{"problem_structure": "routing", "vehicle_count": "one"}` → prefer `traveling-salesman, local-search`, avoid `vehicle-routing`. Single route TSP-like unless timing/other constraints change the structure
- **routing-multi** when `{"problem_structure": "routing", "vehicle_count": "multiple"}` → prefer `vehicle-routing, local-search`, avoid `traveling-salesman`. Multi-vehicle routing is not single TSP
- **routing-directed** when `{"problem_structure": "routing", "travel_cost_directional": true}` → prefer `vehicle-routing, traveling-salesman`, avoid `(none)`. Reverse-segment 2-opt delta cannot assume symmetry; recompute directed arcs
- **schedule-cumulative** when `{"problem_structure": "scheduling", "has_resource_constraints": true}` → prefer `resource-schedule, constraint-sat`, avoid `interval-schedule`. Resource capacity invalidates simple interval-scheduling greedies
- **schedule-simple** when `{"problem_structure": "scheduling", "has_resource_constraints": false}` → prefer `interval-schedule, precedence-dag`, avoid `(none)`. Determine whether objective is cardinality or weighted value
- **resource-fractional** when `{"problem_structure": "resource_allocation", "decision_variable_type": "continuous"}` → prefer `linear-programming`, avoid `mixed-integer`. Use LP only if constraints and objective are linear
- **resource-discrete** when `{"problem_structure": "resource_allocation", "decision_variable_type": "integer"}` → prefer `mixed-integer, constraint-sat`, avoid `linear-programming`. LP relaxation may bound but does not satisfy integrality
- **budget-selection** when `{"problem_structure": "knapsack"}` → prefer `knapsack`, avoid `(none)`. 0/1 vs fractional knapsack differs
- **opt-uncertain** when `{"uncertainty_model": "scenarios"}` → prefer `robust-optimization, multiobjective`, avoid `(none)`. Scenario assumptions and set must be explicit
- **opt-probabilistic** when `{"uncertainty_model": "probability"}` → prefer `stochastic-optimization`, avoid `(none)`. Estimate probability model and test out-of-sample draws
- **ml-temporal** when `{"task_subtype": "time_series_forecast"}` → prefer `forecasting`, avoid `classification`. Walk-forward split required; avoid random shuffle leakage
- **ml-classify** when `{"task_subtype": "classification"}` → prefer `classification`, avoid `regression`. Use held-out classification metrics and calibration
- **ml-regress** when `{"task_subtype": "regression"}` → prefer `regression`, avoid `classification`. Continuous numeric target requires regression loss
- **ml-hypothesis** when `{"task_subtype": "hypothesis_test"}` → prefer `hypothesis-test`, avoid `classification`. Define sampling units and estimand before picking test
- **vision-alignment** when `{"task_subtype": "image_comparison"}` → prefer `image-registration, image-compare`, avoid `image-segmentation`. Align first; do not label registration shift as defect
- **vision-segmentation** when `{"task_subtype": "segmentation"}` → prefer `image-segmentation, image-annotation`, avoid `(none)`. Need labeled masks and negative controls
- **physics-ode** when `{"task_subtype": "ode"}` → prefer `physics-ode, physics-units`, avoid `physics-pde`. Initial conditions and residual required
- **physics-pde** when `{"task_subtype": "pde"}` → prefer `physics-pde, physics-units`, avoid `physics-ode`. Boundary conditions and mesh convergence required
- **document-retrieve** when `{"task_subtype": "policy_retrieval"}` → prefer `text-index, report-provenance`, avoid `(none)`. Citation must trace to correct version/date
- **app-auth** when `{"requires_role_authorization": true}` → prefer `role-access, input-validation`, avoid `(none)`. Enforce authorization server-side, not only screen hiding
- **app-calc** when `{"requires_api_calculation": true}` → prefer `api-python, input-validation`, avoid `frontend-static`. Test a real API call and computation not static UI
- **runtime-no-docker** when `{"docker_available": false}` → prefer `runtime-diagnose`, avoid `container-choice`. Use direct runtime; do not force docker in restricted environment
- **offline-no-external** when `{"network_allowed": false}` → prefer `runtime-diagnose`, avoid `semantic-retrieval`. No remote API/CDN assumption
