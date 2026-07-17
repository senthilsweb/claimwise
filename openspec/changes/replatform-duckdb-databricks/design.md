# Design

## Decisions

| # | Decision | Choice | Rationale |
|---|---|---|---|
| D1 | Dev warehouse | DuckDB local file (`rcm.duckdb`) | Zero infra; Postgres-compatible quoting so no model rewrites |
| D2 | Prod warehouse | Databricks (Unity Catalog, Delta) | Governed lakehouse for marts; adapter is a pure-Python wheel |
| D3 | Dev runs bare, Docker is the prod runner | No containers for dev | DuckDB needs none; image ships dbt + adapters + Elementary CLI |
| D4 | Elementary prod-only | `+enabled: "{{ target.name == 'prod' }}"` | Elementary does not support DuckDB; dev keeps schema + singular tests |
| D5 | Keep double-quoted identifiers | No mass rewrite of 24 model files | Works on DuckDB today; Databricks needs `spark.sql.ansi.doubleQuotedIdentifiers=true` (set via profile `session_properties`; verify on your warehouse channel) |
| D6 | Aggregation portability | `dbt.listagg` (cross-db macro, in dbt-core since dbt_utils 1.0) | Renders per-adapter `listagg`/`string_agg` — DuckDB, Databricks SQL (2024.50+), Snowflake (phase 2 comes free) |
| D7 | Phase 2 Snowflake | New profile output + `dbt-snowflake` only | All SQL fixes chosen to be Snowflake-safe; quoted identifiers preserve case there too |

## Environment Contract
All configuration flows through these variables (see `.env.example`):

| Variable | Default | Used by |
|---|---|---|
| `DBT_TARGET` | `dev` | Makefile, entrypoint |
| `DUCKDB_PATH` | `rcm.duckdb` | dev target |
| `DATABRICKS_HOST` | — (required for prod) | prod target |
| `DATABRICKS_HTTP_PATH` | — (required for prod) | prod target |
| `DATABRICKS_TOKEN` | — (required for prod) | prod target |
| `DATABRICKS_CATALOG` | `rcm` | prod target |
| `ENABLE_ELEMENTARY` | `true` | entrypoint (prod only) |

## Command Contract
- **Make**: `setup deps debug seed run test build docs report daily clean docker-build docker-daily` — all accept `TARGET=prod` (default `dev`).
- **Docker entrypoint**: `daily` (default) | `build` | `run` | `test` | `seed` | `dbt <args>`; validates Databricks env vars; Elementary report to `/app/reports`.

## Risks
- **R1**: Double-quoted identifiers on Databricks (D5) — needs smoke test with real credentials; fallback is enabling the session property or a one-off quoting normalization.
- **R2**: `dbt_utils.listagg` on older Databricks SQL channels — requires LISTAGG support (2024.50+).
- **R3**: `dbt_external_tables` package appears unused — remove; restore if any run-operation depends on it.
