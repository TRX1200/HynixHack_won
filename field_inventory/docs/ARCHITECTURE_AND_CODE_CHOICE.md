# Architecture / code-choice policy

The highest leverage is **choosing the smallest correct code pattern**, not adding a framework. Use existing repository conventions first. For a new greenfield project:

| Task shape | Default code shape | Add only if | Verification |
|---|---|---|---|
| One-off CSV or JSON | Python CLI (`csv`, `json`, `sqlite3`) | pandas/DuckDB is already installed or clearly faster | deterministic rerun and roundtrip |
| Data-intensive statistical pipeline | Python scripts + results JSON | web UI required by task | fixed seed, granularity and missingness |
| Simple interactive calculator | Single HTML/CSS/JS page | server-side privileged logic or heavy compute | browser input/output and pure-function tests |
| Web app with calculation engine | Python HTTP API + vanilla JS, or existing Node stack | React/TS needed for existing code or complex state | actual HTTP status+schema + Browser manual click |
| Rich chart/report | Matplotlib/HTML, static SVG | interactions specifically required | unit labels, source/uncertainty, export check |
| Document/policy workflow | SQLite FTS5, source spans, rule tables | semantic model allowed/local and justified | quote resolves, contradiction table |
| Image measurement | Pillow/OpenCV classical pipeline | deep model authorized and available | calibration and labeled negative controls |
| Assignment/routing | Fast heuristic + independent verifier | exact solver installed/time budget allows | constraints + baseline objective vs improved |
| Scientific solver | SymPy/NumPy/SciPy | physics software/solver only if required | dimension, residual, limiting-case, convergence |
| Multi-component service | Existing framework, one vertical slice | Compose only if multiple services benefit | direct start fallback |

## Choice gates

1. Does README mandate stack, specific file or interface? Follow explicit instructions.
2. What executable/runtime is **actually** installed? Check python/python3/node versions in the provided terminal. Run the Python doctor only after confirming a supported Python; otherwise read Markdown guidance and preserve the existing task language.
3. Can standard library solve it within constraints? Prefer it when reliable.
4. Is there a performance bottleneck **measured**? If not, avoid C++/Rust/microservices solely for prestige.
5. Is data permitted to leave local environment? If no, external API calls are disallowed.
6. Is Docker available and authorized? If no, direct CLI server; never alter management controls.
7. Can each language boundary be described by a versioned JSON schema? If no, simplify boundaries.

## API / pipeline invariants

IDs remain strings when leading zero or notation matters. Nullable is not zero. Units are explicit. Keep `schema_version`, `source_row_id`, timestamps/timezone when relevant, stable error schema, and request contract. One source of truth for constants, with runtime validation on both boundaries.

## Handoff plan

Frontend owns UI source files; backend owns server/calculation; reviewer owns independent input/oracle/tests; recorder owns task status/decision log. Fix contract before parallel work. Keep conflict-free file ownership and integrate early.
