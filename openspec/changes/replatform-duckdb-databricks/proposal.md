# Proposal: Replatform from Postgres to DuckDB (dev) + Databricks (prod)

## Why
- Postgres adds container overhead for dev and offers no path to a governed lakehouse for prod.
- DuckDB gives zero-infrastructure local development (a single file, no Docker needed for dev).
- Databricks (Unity Catalog + Delta) is the production target for persisted marts; Snowflake is planned as a swappable alternative in phase 2.
- Credentials are currently hardcoded in `profiles.yml` — must move to environment variables.

## What Changes
- **Remove Postgres entirely**: delete `docker-compose-pg.yml`, Postgres targets, hardcoded credentials.
- **New targets**: `dev` = DuckDB (`rcm.duckdb`), `prod` = Databricks — both env-var driven.
- **Dialect portability**: replace `string_agg` with `dbt_utils.listagg`, `null::timestamp` with `cast(null as timestamp)`.
- **Dockerize**: prod runner image + entrypoint (`daily | build | run | test | seed | dbt`), compose file.
- **Simple Makefile**: setup / build / test / daily targets, `TARGET=prod` switch.
- **Elementary**: upgrade to 0.20.x, enabled on prod only (Elementary does not support DuckDB).
- **Tests**: add singular data-quality tests (empty today).
- **Docs**: rewrite README — short quick-start only.

## Impact
- Affected specs: `warehouse-targets` (new), `pipeline-operations` (new)
- Affected code: `profiles.yml`, `dbt_project.yml`, `packages.yml`, 7 model files, `requirements.txt` (replaces misspelled `reqirements.txt`), new Docker/Make/env files, `tests/`, `README.md`
- Not affected: model DAG, seeds, macros, schema naming
