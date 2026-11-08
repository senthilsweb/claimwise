# Claimwise rules for Maia

Claimwise is a healthcare revenue cycle management (RCM) demo. Build it as **native Matillion pipelines on Databricks**. The dbt files under `dbt-pipeline/` are the written specification only.

## Hard rules
- Never use the dbt Core component. Never run dbt. Rebuild every model as a transformation pipeline.
- Target Unity Catalog catalog `claimwise`. Schemas: `landing` (volume only), `bronze`, `silver`, `gold`. Create no other schemas.
- Write unquoted identifiers only. Never double-quote identifiers: Databricks serverless SQL treats `"x"` as a string literal.
- Every target is a full-refresh table (Rewrite Table / CREATE OR REPLACE TABLE). No views, no incremental loads, no snapshots.
- Keep source camelCase column names in bronze and in `stg_*` tables. Use snake_case output names in `int_*` and gold exactly as the spec SQL aliases them.
- Stop at gold. Do not build dashboards, metric views, or downstream consumers.
- Do not read `dbt-pipeline/seeds/`, `macros/`, `dbt_project.yml`, `profiles.yml`, `packages.yml`: they are dbt runtime files, not spec.

## Layers and tables
| Layer | Tables | Source |
|---|---|---|
| landing | volume `claimwise.landing.raw/<table>/<table>.csv` | 7 CSVs: users, facilities, encounters, health_plans, claims, activities, collections |
| bronze | 7 tables, same names as the CSVs | `matillion/sql/10_bronze_load.sql` (one SQL Script component per table, run that SQL verbatim) |
| silver | `stg_users, stg_facilities, stg_encounters, stg_health_plans, stg_claims, stg_activities, stg_collections` then `int_patients, int_doctors, int_staff, int_payers` | `dbt-pipeline/models/silver/**/*.sql` |
| gold | `dim_date, dim_department, dim_facility, dim_health_plan, dim_staff, dim_diagnosis, dim_doctor, dim_patient, fct_encounters, dim_payer, fct_claims, fct_claim_activities, fct_collections` and metrics `mtr_executive_summary, mtr_claims_funnel, mtr_revenue_monthly, mtr_payer_scorecard, mtr_ar_aging, mtr_department_activity` | `dbt-pipeline/models/gold/**/*.sql` |

## Pipeline layout
- Folder `pipelines/claimwise/`. Orchestration: `00_claimwise_daily` (master) calls `10_bronze_load`, `20_silver`, `30_gold` in order; fail fast on any error.
- One transformation pipeline per target table, named exactly like the table (for example `stg_claims`, `fct_claims`). Inside each layer run independent tables in parallel and respect dependencies: `stg_*` before `int_*`; `dim_*`/`fct_*` before `mtr_*`.
- End every transformation pipeline with one Rewrite Table component writing `claimwise.<schema>.<table>`.
- Prefer Table Input, Filter, Join, Calculator, Aggregate, Rank, Rewrite Table. Use SQL components only when the spec needs a function the visual components lack.

## Translating dbt Jinja to Databricks SQL
- `{{ source('bronze', t) }}` → `claimwise.bronze.<t>`. `{{ ref(m) }}` → `claimwise.silver.<m>` for stg/int, `claimwise.gold.<m>` otherwise.
- `{{ dbt.listagg(measure='x', delimiter_text="', '") }}` → `array_join(collect_set(x), ', ')`.
- `{{ dbt.datediff(a, b, 'day') }}` → `datediff(b, a)`.
- `{{ dbt.date_trunc('month', x) }}` → `date_trunc('MONTH', x)`.
- `dbt_date.get_date_dimension('2024-01-01','2026-12-31')` → `select explode(sequence(DATE'2024-01-01', DATE'2026-12-31', INTERVAL 1 DAY)) as date_day`. Then: `year(date_day)`, `month(date_day)`, `date_format(date_day,'MMMM')` month_name, `quarter(date_day)`, `dayofweek(date_day)`, `date_format(date_day,'EEEE')` day_name, `is_weekend = dayofweek(date_day) in (1,7)`, `week_start_date = date_trunc('WEEK', date_day)`, `week_end_date = date_add(date_trunc('WEEK', date_day), 6)`.
- `{{ config(...) }}` lines carry no logic: ignore them.
- `current_timestamp as valid_from, cast(null as timestamp) as valid_to, true as is_current` stay as literal Calculator expressions.

## Known spec defect
`dbt-pipeline/models/gold/clinical/dim_doctor.sql` is an accidental copy of `dim_diagnosis`. Build `dim_doctor` from `claimwise.silver.int_doctors` instead, with columns: doctor_id, doctor_code, doctor_name, specialty, contact_info (from contactInfo), total_patients_seen, unique_patients_seen, last_encounter_date, facilities_practiced_in, facility_names, valid_from, valid_to, is_current.

## Data quality
Add Matillion tests after silver: not null and unique on every `id` and business code (`userID, claimID, collectionID, encounterID, activityID, facilityID, healthPlanID`); accepted values for `users.userType` (PATIENT, DOCTOR, STAFF, PAYER), `claims.status` (Submitted, In Review, Approved, Denied, Appealed), `encounters.type`, `activities.activityType`, `collections.status`, `collections.methodOfCollection` as listed in `dbt-pipeline/models/silver/_silver_models.yml`. Translate the singular tests in `dbt-pipeline/tests/*.sql` into Assert/Query tests after gold: a failing test must fail the run.

## Expected results after a full run
`claimwise.gold.mtr_executive_summary` must show claim_count 5000, encounter_count 8000, gross_billed 12601107.12, collection_rate_pct 48.02, denial_rate_pct 14.62, open_ar 4729526.38. `mtr_claims_funnel` must show Approved 3054, Denied 731, In Review 598, Submitted 469, Appealed 148. Use `matillion/sql/90_verify.sql` to check.

## Git
Work on branch `matillion`. Commit after each layer with a message that names the layer. Never commit `.env` or credentials.
