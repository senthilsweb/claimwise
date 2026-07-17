# Spec Delta: warehouse-targets

## ADDED Requirements

### Requirement: Development runs on DuckDB with zero infrastructure
The project SHALL build end-to-end on a local DuckDB file with no running services.

#### Scenario: Fresh clone dev build
- **WHEN** a developer runs `make setup deps seed build` on a fresh clone
- **THEN** all models and tests pass against `rcm.duckdb` without any container or server

### Requirement: Production persists marts to Databricks
The `prod` target SHALL materialize all layers in Databricks Unity Catalog, with marts as Delta tables.

#### Scenario: Prod build
- **WHEN** `dbt build --target prod` runs with `DATABRICKS_*` variables set
- **THEN** models land under `<catalog>.raw|staging|intermediate|mart` as Delta objects

### Requirement: No hardcoded credentials
All connection settings SHALL come from environment variables; `profiles.yml` contains no secrets.

#### Scenario: Missing prod credentials
- **WHEN** a prod command runs without `DATABRICKS_HOST/HTTP_PATH/TOKEN`
- **THEN** it fails fast with a clear message naming the missing variables

### Requirement: SQL is warehouse-portable
Model SQL SHALL avoid dialect-specific functions; aggregations use `dbt_utils` cross-database macros so a Snowflake target can be added without model changes.
