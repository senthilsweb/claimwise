# Spec: metric-layer

## ADDED Requirements

### Requirement: KPI aggregation is defined once in the gold metric models
All business KPI computation (collection rate, denial rate, open AR, aging buckets, cycle days) SHALL live in `models/gold/metrics/mtr_*` dbt models. Consumers SHALL select from these models without re-aggregating.

#### Scenario: Dashboard widget reads a KPI
- **WHEN** a dashboard counter shows the collection rate
- **THEN** it selects `collection_rate_pct` from `mtr_executive_summary` and performs no arithmetic of its own

### Requirement: Metric models run on both targets
Metric models SHALL build green on DuckDB (dev) and Databricks (prod) with portable SQL (`dbt.datediff`, no engine-specific functions, unquoted identifiers).

#### Scenario: Local build
- **WHEN** `make build` runs on the dev target
- **THEN** all `mtr_*` models and their tests pass

### Requirement: Unity Catalog metric view is attempted, not assumed
A `create_metric_view` macro SHALL attempt `gold.claimwise_metrics`; if the platform rejects metric views, the failure SHALL be reported and the `mtr_*` models remain the semantic layer of record.

#### Scenario: Metric views unavailable on Free Edition
- **WHEN** `CREATE VIEW ... WITH METRICS` fails
- **THEN** the pipeline and dashboard are unaffected and the outcome is documented
