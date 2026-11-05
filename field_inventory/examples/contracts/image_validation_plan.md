# Task-specific validation plan: synth-image

**Status: PLAN ONLY — NOTHING TESTED**

Every row requires independent implementation, actual execution and evidence; missing tests remain `NOT_RUN`.

| ID | Family | Kind | Required case | Initial status |
|---|---|---|---|---|
| `computer_vision:P01` | computer_vision | positive | known marked or synthetic shape | NOT_RUN |
| `computer_vision:N01` | computer_vision | negative | shift-only unchanged image | NOT_RUN |
| `computer_vision:N02` | computer_vision | negative | contrast-only difference | NOT_RUN |
| `computer_vision:N03` | computer_vision | negative | wrong scale | NOT_RUN |
| `reporting:P01` | reporting | positive | number re-derived from supplied synthetic data | NOT_RUN |
| `reporting:N01` | reporting | negative | unlinked claim | NOT_RUN |
| `reporting:N02` | reporting | negative | broken font | NOT_RUN |
| `reporting:N03` | reporting | negative | mismatched summary figure | NOT_RUN |

## Unresolved
- physical pixel-to-mm calibration not provided

## Reviewer instructions

For each test: record source evidence, independent expected value, code path, test command, exit status and log. Inject deliberate negative cases. Never change NOT_RUN to PASS based only on a model assertion.

