# Claimwise rules for Maia

Claimwise is a healthcare revenue cycle management (RCM) demo built as **native Matillion pipelines on Databricks**. The pipelines under `pipelines/claimwise/` are the source of truth; change them, do not rebuild from scratch.

## Hard rules
- Never use the dbt Core component. Never run dbt. Everything is a transformation or orchestration pipeline.
- Target Unity Catalog catalog `claimwise`. Schemas: `landing` (volume only), `bronze`, `silver`, `gold`. Create no other schemas.
- Write unquoted identifiers only. Never double-quote identifiers: Databricks serverless SQL treats `"x"` as a string literal.
- Every target is a full-refresh table (Rewrite Table / CREATE OR REPLACE TABLE). No views, no incremental loads, no snapshots.
- Keep source camelCase column names in bronze and in `stg_*` tables. Use snake_case output names in `int_*` and gold.
- Stop at gold. Do not build dashboards, metric views, or downstream consumers unless asked.

## Layers and tables
| Layer | Tables | Built by |
|---|---|---|
| landing | volume `claimwise.landing.raw/<table>/<table>.csv` | `data/landing/*.csv` uploaded with `matillion/scripts/dbx.py put` |
| bronze | users, facilities, encounters, health_plans, claims, activities, collections | `10_bronze_load` (one SQL Script per table, SQL also in `matillion/sql/10_bronze_load.sql`) |
| silver | `stg_users, stg_facilities, stg_encounters, stg_health_plans, stg_claims, stg_activities, stg_collections` then `int_patients, int_doctors, int_staff, int_payers` | `20_silver` and the `stg_*.tran.yaml` / `int_*.tran.yaml` pipelines |
| gold | `dim_date, dim_department, dim_facility, dim_health_plan, dim_staff, dim_diagnosis, dim_doctor, dim_patient, dim_payer, fct_encounters, fct_claims, fct_claim_activities, fct_collections` and metrics `mtr_executive_summary, mtr_claims_funnel, mtr_revenue_monthly, mtr_payer_scorecard, mtr_ar_aging, mtr_department_activity` | `30_gold` and the `dim_*`, `fct_*`, `mtr_*` pipelines |

## Pipeline layout
- Folder `pipelines/claimwise/`. Orchestration: `00_claimwise_daily` (master) calls `10_bronze_load`, `20_silver`, `30_gold` in order; fail fast on any error.
- One transformation pipeline per target table, named exactly like the table. Inside each layer run independent tables in parallel and respect dependencies: `stg_*` before `int_*`; `dim_*`/`fct_*` before `mtr_*`.
- End every transformation pipeline with one Rewrite Table component writing `claimwise.<schema>.<table>`.
- Prefer Table Input, Filter, Join, Calculator, Aggregate, Rank, Rewrite Table. Use SQL components only when a function the visual components lack is needed.
- Data quality: the `20_silver` asserts (not null, unique, accepted values) and the `30_gold` singular-test assertions must keep failing the run on any violation. Add a test when you add a column rule.

## Databricks SQL idioms used here
- String aggregation: `array_join(collect_set(x), ', ')`.
- Day difference: `datediff(end_date, start_date)`.
- Month bucket: `date_trunc('MONTH', x)`.
- Date spine (`dim_date`): `select explode(sequence(DATE'2024-01-01', DATE'2026-12-31', INTERVAL 1 DAY)) as date_day`, then `year()`, `month()`, `date_format(date_day,'MMMM')`, `quarter()`, `dayofweek()`, `date_format(date_day,'EEEE')`, `is_weekend = dayofweek(date_day) in (1,7)`, `week_start_date = date_trunc('WEEK', date_day)`, `week_end_date = date_add(date_trunc('WEEK', date_day), 6)`.
- SCD placeholders: `current_timestamp as valid_from, cast(null as timestamp) as valid_to, true as is_current`.

## Expected results after a full run
`claimwise.gold.mtr_executive_summary` must show claim_count 5000, encounter_count 8000, gross_billed 12601107.12, collection_rate_pct 48.02, denial_rate_pct 14.62, open_ar 4729526.38. `mtr_claims_funnel` must show Approved 3054, Denied 731, In Review 598, Submitted 469, Appealed 148. Use `matillion/sql/90_verify.sql` to check. These numbers belong to the checked-in `data/landing` CSVs; regenerating the data changes them.

## Git
Work on a branch off `feature/claimwise-matillion`. Commit after each logical change with a message that names the layer. Never commit `.env` or credentials.
