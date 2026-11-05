# data inventory — 10 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`file-ingestion`](../recipes/file-ingestion.md) | File inventory and schema profiling | File manifest, type/sample row counts | Missing/encoding/empty/header test |
| [`csv-join`](../recipes/csv-join.md) | Multi-table joins and key checks | Validate unique keys, cardinality and missing matches | Unmatched keys, join explosion, duplicates |
| [`csv-clean`](../recipes/csv-clean.md) | Missing/duplicate/outlier cleaning | Data quality report before mutation | Before/after counts and immutable raw source |
| [`json-normalize`](../recipes/json-normalize.md) | Nested JSON normalization | Explicit flattening with full parent IDs | Roundtrip IDs and array multiplicity |
| [`sql-analytic`](../recipes/sql-analytic.md) | Analytical SQL and grouping | SQLite or DuckDB query with explicit grain | Conservation of counts, null semantics |
| [`etl-batch`](../recipes/etl-batch.md) | Deterministic ETL pipeline | Idempotent staged transforms | Repeat run equal hash, failure recovery |
| [`text-index`](../recipes/text-index.md) | Local text search | Literal search with source offsets | Quoted evidence resolves to real source span |
| [`semantic-retrieval`](../recipes/semantic-retrieval.md) | Semantic document retrieval | Token/FTS retrieval without model | Recall tests with relevant synthetic passages |
| [`spatial-nearest`](../recipes/spatial-nearest.md) | Nearest coordinate candidates | Haversine for straight-line geographic distance | Bounds, symmetry and coordinate sanity |
| [`spatial-cluster`](../recipes/spatial-cluster.md) | Spatial clustering | Fixed radius groups with geographic units | Cluster stability and outlier tests |
