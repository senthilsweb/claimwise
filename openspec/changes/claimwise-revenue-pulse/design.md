# Design: Claimwise Revenue Pulse

## Metric layer

All KPI aggregation is computed once in dbt gold models (`models/gold/metrics/`), materialized as tables on both targets. Consumers (dashboard widgets, future notebooks/Genie) select columns — they never re-aggregate.

| Model | Grain | Key columns |
|---|---|---|
| `mtr_executive_summary` | 1 row | gross_billed, total_collected, collection_rate_pct, denial_rate_pct, open_ar, avg_cycle_days, claim_count, encounter_count |
| `mtr_revenue_monthly` | month | billed_amount, collected_amount, collection_rate_pct, claim_count, denied_count |
| `mtr_payer_scorecard` | payer | billed, collected, collection_rate_pct, denial_rate_pct, open_ar, claim_count, avg_claim_amount |
| `mtr_ar_aging` | payer × aging bucket | open_claim_count, open_ar_amount (buckets 0-30/31-60/61-90/90+) |
| `mtr_claims_funnel` | claim status | claim_count, total_amount, pct_of_claims |
| `mtr_department_activity` | specialty | encounter_count, unique_patients, active_doctors, avg_duration_minutes |

Business definitions (single source of truth):
- **Collection rate** = collected / billed (collections joined to claims; monthly grain uses calendar month of each side).
- **Denial rate** = denied claims / all claims.
- **Open AR** = claim_amount − collected for claims not Denied, where remainder > 0. Aging bucketed on days since claim_date via `dbt.datediff` (portable DuckDB/Databricks).
- **Avg cycle days** = dateUpdated − dateCreated on claims.

UC metric view `gold.claimwise_metrics` is attempted via `dbt run-operation create_metric_view` (measures/dimensions over fct_claims + fct_collections). Free Edition availability is unverified — the `mtr_*` models are the layer of record either way.

## Dashboard

Databricks AI/BI Dashboard, serialized as `dashboards/claimwise-revenue-pulse.lvdash.json` in the repo (dashboard-as-code). Datasets are thin `SELECT`s over `{catalog}.gold.mtr_*`. Three pages:

1. **Executive Overview** — 6 KPI counters (from mtr_executive_summary), billed-vs-collected monthly trend (line), claim status mix (pie), AR aging (bar).
2. **Claims Operations** — funnel bar from mtr_claims_funnel, denial/appeal breakdown, monthly claim volume, open-claims work table (top open AR by payer, from mtr_payer_scorecard + mtr_ar_aging).
3. **Payers & Providers** — payer scorecard table, AR by payer × bucket (grouped bar), department activity (bar + table).

Deployment: `dashboards/deploy.py` uses databricks-sdk (already a dbt-databricks dependency) with `DATABRICKS_HOST/TOKEN`; warehouse id parsed from `DATABRICKS_HTTP_PATH`; create-or-update by display name, then publish (embedded credentials). Catalog name substituted from `DATABRICKS_CATALOG` at deploy time so the JSON stays environment-free.

## Lineage

- Observed: widgets query gold tables through the SQL warehouse → Unity Catalog links the dashboard to `gold.mtr_*` → back to bronze.
- Declared: `models/dashboard.yml` exposure updated (name `claimwise_revenue_pulse`, real URL, depends_on the `mtr_*` models).

## Decisions
- Revenue-by-specialty is intentionally omitted: claims are not linked to encounters in the source schema; joining via patientID would fabricate revenue attribution. Department activity shows volumes only.
- Dashboard theme: default light canvas; Claimwise branding via markdown header widgets and consistent titles (AI/BI theming API is limited and not worth a dependency).
