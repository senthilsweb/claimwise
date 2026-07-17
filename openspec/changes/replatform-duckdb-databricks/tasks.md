# Tasks (AI-DLC Bolts)

AI-DLC mapping: **Inception** = proposal + design (done) · **Construction** = bolts B1–B5, run by parallel subagents on disjoint file sets · **Operations** = B6 validation by the orchestrating agent.

## B1. Config & Dialect (subagent: config)
- [x] 1.1 Rewrite `profiles.yml`: `dev` DuckDB + `prod` Databricks, env-var driven; matching `elementary` profile; add `profiles.yml.example`
- [x] 1.2 Create `.env.example` per environment contract
- [x] 1.3 `dbt_project.yml`: gate Elementary to prod, add builtin-materialization override flag
- [x] 1.4 `packages.yml`: Elementary → 0.20.0, drop unused `dbt_external_tables`
- [x] 1.5 New lean `requirements.txt`; delete `reqirements.txt`, `docker-compose-pg.yml`
- [x] 1.6 Fix `string_agg` → `dbt_utils.listagg` (2 files); `null::timestamp` → `cast(null as timestamp)` (5 files)

## B2. Containerization (subagent: docker)
- [x] 2.1 `Dockerfile` (python slim, dbt-duckdb + dbt-databricks + elementary CLI, dbt deps baked in)
- [x] 2.2 `docker-entrypoint.sh` per command contract
- [x] 2.3 `.dockerignore`, `docker-compose.yml` (dbt service, `.env` file, reports volume)

## B3. Makefile (subagent: make)
- [x] 3.1 Simple Makefile (~15 targets) per command contract, `TARGET=dev|prod`

## B4. Tests (subagent: tests)
- [x] 4.1 3–4 singular data-quality tests in `tests/` (portable SQL only)

## B5. Docs (subagent: docs)
- [x] 5.1 Rewrite `README.md`: short quick-start (dev DuckDB, prod Databricks/Docker), no extra details

## B6. Validation (orchestrator)
- [x] 6.1 Fresh venv → `dbt deps && dbt seed && dbt build --target dev` on DuckDB, green
- [x] 6.2 Reconcile subagent output, fix fallout, mark tasks complete
