# Task-specific validation plan: synth-route

**Status: PLAN ONLY — NOTHING TESTED**

Every row requires independent implementation, actual execution and evidence; missing tests remain `NOT_RUN`.

| ID | Family | Kind | Required case | Initial status |
|---|---|---|---|---|
| `optimization:P01` | optimization | positive | nonempty known-feasible synthetic case | NOT_RUN |
| `optimization:N01` | optimization | negative | infeasible capacity/coverage | NOT_RUN |
| `optimization:N02` | optimization | negative | duplicate item | NOT_RUN |
| `optimization:N03` | optimization | negative | asymmetric cost matrix | NOT_RUN |
| `geospatial:P01` | geospatial | positive | known coordinate pair and permitted travel matrix | NOT_RUN |
| `geospatial:N01` | geospatial | negative | swapped lat/lon | NOT_RUN |
| `geospatial:N02` | geospatial | negative | unreachable or obstacle-separated points | NOT_RUN |
| `R001` | requirements | invariant | Verify explicitly stated constraint: all stops visited | NOT_RUN |
| `R002` | requirements | invariant | Verify explicitly stated constraint: vehicle loads within limit | NOT_RUN |

## Unresolved
- None supplied; review missing information explicitly.

## Reviewer instructions

For each test: record source evidence, independent expected value, code path, test command, exit status and log. Inject deliberate negative cases. Never change NOT_RUN to PASS based only on a model assertion.

