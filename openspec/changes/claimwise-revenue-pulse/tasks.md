# Tasks (AI-DLC Bolts)

AI-DLC mapping: **Inception** = proposal + design (done) · **Construction** = bolts B1–B4 · **Operations** = B5 validation against the live workspace.

## B1. Metric layer (dbt)
- [x] 1.1 `models/gold/metrics/`: mtr_executive_summary, mtr_revenue_monthly, mtr_payer_scorecard, mtr_ar_aging, mtr_claims_funnel, mtr_department_activity (portable SQL, `dbt.datediff`)
- [x] 1.2 `_metrics_models.yml`: descriptions + not_null/unique tests on grain keys
- [x] 1.3 Local `make build` green on DuckDB
- [x] 1.4 `make build TARGET=prod` green on Databricks

## B2. Dashboard definition
- [x] 2.1 `dashboards/claimwise-revenue-pulse.lvdash.json` — 3 pages, KPI counters, line/bar/pie, tables, markdown branding headers

## B3. Deploy tooling
- [x] 3.1 `dashboards/deploy.py` (databricks-sdk, create-or-update by name, publish)
- [x] 3.2 `make dashboard TARGET=prod` target
- [x] 3.3 Deploy to workspace; iterate until API accepts and dashboard renders

## B4. Semantic layer + lineage wiring
- [x] 4.1 `create_metric_view` macro; attempt `gold.claimwise_metrics` on prod; record availability outcome
- [x] 4.2 Update `models/dashboard.yml` exposure (name, URL, mtr_* deps)
- [x] 4.3 README notes (dbt-pipeline + dashboards folder)

## B5. Validation (operations)
- [x] 5.1 All widgets query successfully against `workspace.gold`
- [x] 5.2 Unity Catalog lineage on fct_claims/mtr_* shows the dashboard downstream (user visual check)
- [x] 5.3 Update project memory
