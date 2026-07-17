# Proposal: Claimwise Revenue Pulse — Databricks AI/BI Dashboard over the Gold Layer

## Why
- The pipeline is verified end-to-end on Databricks (bronze/silver/gold, 220 green checks) but nothing consumes the gold layer inside the platform — the lineage story stops at the tables.
- A native AI/BI Dashboard extends Unity Catalog lineage one hop further: Dashboard → gold → silver → bronze, all visible in Catalog Explorer. No external BI tool, works on Free Edition serverless.
- KPI math (collection rate, denial rate, AR aging) must be defined once — a metric/semantic layer — not recomputed per widget, per consumer.

## What Changes
- **Metric layer (dbt)**: new `models/gold/metrics/` with `mtr_*` models — executive summary, revenue monthly, payer scorecard, AR aging, claims funnel, department activity. All KPI aggregation lives here; dashboards and any future consumer read them as-is.
- **UC metric view (attempt)**: `gold.claimwise_metrics` created via a dbt macro; if metric views are unavailable on Free Edition, the `mtr_*` models are the semantic layer and the macro documents the gap.
- **Dashboard as code**: `dashboards/claimwise-revenue-pulse.lvdash.json` — 3 pages (Executive Overview, Claims Operations, Payers & Providers) with KPI counters, trend/bar/pie charts, and work-list tables. Claimwise-themed naming and layout.
- **Deploy tooling**: `dashboards/deploy.py` (databricks-sdk, env-var driven) + `make dashboard TARGET=prod`.
- **Lineage wiring**: dbt exposure in `dashboard.yml` re-pointed to the deployed dashboard URL and `mtr_*` dependencies, so declared (dbt) and observed (Unity Catalog) lineage match.

## Impact
- Affected specs: `business-dashboards` (new), `metric-layer` (new)
- Affected code: new `models/gold/metrics/`, new `dashboards/`, `Makefile`, `models/dashboard.yml`, READMEs
- Not affected: existing models, tests, seeds, generator, targets/profiles
