# Spec Delta: pipeline-operations

## ADDED Requirements

### Requirement: Dockerized prod runner
A Docker image SHALL run the pipeline against Databricks with commands `daily | build | run | test | seed | dbt <args>`; `daily` runs build → Elementary tables → HTML report and still produces the report when some models fail.

#### Scenario: Daily run
- **WHEN** `docker compose run dbt daily` executes with a valid `.env`
- **THEN** models build, tests run, and `reports/elementary_report.html` is written

### Requirement: Simple Make interface
A Makefile SHALL expose setup/build/test/daily targets, defaulting to the DuckDB dev target and switching with `TARGET=prod`.

#### Scenario: Target switch
- **WHEN** `make build TARGET=prod` runs
- **THEN** dbt executes with `--target prod`

### Requirement: Observability on prod only
Elementary models SHALL be enabled only for the prod target, since Elementary does not support DuckDB.

### Requirement: Singular data-quality tests
The `tests/` directory SHALL contain singular tests covering claim amounts, encounter date ordering, and dimension key uniqueness, written in portable SQL.
