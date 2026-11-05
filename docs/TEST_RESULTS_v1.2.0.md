# Actual validation record — v1.2.0

Date: 2026-10-31. This review ran on Windows, Python 3.12.14, Node v24.13.0.
No package, browser, model, or system runtime was installed during this review.

| Check | Actual result | Scope |
| --- | --- | --- |
| Full unittest discovery | 127 passed, 3 skipped, 0 failures | 130 discovered, including calculator and setup integration |
| Python -S unittest discovery | 119 passed, 11 skipped, 0 failures | Site packages disabled; Node still available separately |
| Local MCP smoke | 6 checks passed | stdio initialize/list/search/read/stats/invalid chunk ID |
| New electronics calculators | 12 tests passed | Known scalar values, scaling, independent Arrhenius reference, invalid input and input preservation |
| Generated MCP configuration | Passed in unittest suite | Actual local executable/server/index paths, subprocess launch and tools/list |
| Python syntax | 27 files passed | AST syntax with Python 3.10 grammar; not an actual Python 3.10 runtime test |
| JSON and release integrity | Verified during packaging | Config/catalog/examples JSON, per-file bytes and SHA-256 |

The full run skipped jsonschema (not installed), PyMuPDF (not installed), and a symlink test
(Windows symlink permission unavailable). The -S run additionally skipped Pillow image tests.
Existing Pillow 12.3.0 was used for the full image checks. No missing package was installed.
The optional numeric_smoke checks all skipped because SymPy/SciPy/Pint were unavailable.
Skipped checks are not passes.

## Corrections actually verified

- Strict JSON duplicate keys and overflow/underflow; malformed CSV quotes.
- Exact bounded Decimal sums and assignment costs beyond 28 digits, aggregate field conflicts.
- DOCX whitespace, Unicode retrieval snippets, extract/load chunk-size consistency.
- Image transparency handling and luminance difference, report status/evidence structure.
- MCP request types, initialization, malformed JSON recovery, UTF-8 under an ASCII locale.
- CLI UTF-8 under an ASCII locale, selected-skill license preservation, duplicate request refusal.
- Formula input fields/units/domain, finite outputs, RC CLI integration, known-value calculator checks.

## Not verified

- Cofa-provided Codex, actual MCP registration, skill discovery, setup persistence or permissions.
- Playwright startup/browser binaries and real browser flow; DuckDB MCP execution and isolation.
- Optional scientific package matrix, complete PDF/OCR support, real process/device/simulation accuracy.
- Any assessment problem, answer, score or improvement in model quality.

The original author's Linux v1.1.0 report is preserved unchanged at docs/TEST_RESULTS_v1.1.0.md.
It is historical supplied evidence, not a fresh Linux rerun by this review.
Machine-readable results are in TEST_RESULTS.json. Package publication status is separate from test success.
