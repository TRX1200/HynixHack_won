# Task-specific validation plan: synth-ode

**Status: PLAN ONLY — NOTHING TESTED**

Every row requires independent implementation, actual execution and evidence; missing tests remain `NOT_RUN`.

| ID | Family | Kind | Required case | Initial status |
|---|---|---|---|---|
| `scientific_computing:P01` | scientific_computing | positive | analytic/manufactured solution with known result | NOT_RUN |
| `scientific_computing:N01` | scientific_computing | negative | unit mismatch | NOT_RUN |
| `scientific_computing:N02` | scientific_computing | negative | wrong sign | NOT_RUN |
| `scientific_computing:N03` | scientific_computing | negative | coarse step instability | NOT_RUN |
| `reporting:P01` | reporting | positive | number re-derived from supplied synthetic data | NOT_RUN |
| `reporting:N01` | reporting | negative | unlinked claim | NOT_RUN |
| `reporting:N02` | reporting | negative | broken font | NOT_RUN |
| `reporting:N03` | reporting | negative | mismatched summary figure | NOT_RUN |
| `R001` | requirements | invariant | Verify explicitly stated constraint: initial condition checked | NOT_RUN |
| `R002` | requirements | invariant | Verify explicitly stated constraint: unit consistency | NOT_RUN |

## Unresolved
- None supplied; review missing information explicitly.

## Reviewer instructions

For each test: record source evidence, independent expected value, code path, test command, exit status and log. Inject deliberate negative cases. Never change NOT_RUN to PASS based only on a model assertion.

