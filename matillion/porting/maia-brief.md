Build the Claimwise lakehouse as native Matillion pipelines on Databricks in this project (environment `dev`, catalog `claimwise`).

FIRST create the context file `.matillion/maia/rules/claimwise.md` with exactly the content between the CONTEXT FILE markers, commit it, and follow every rule in it for the rest of this task.

===== CONTEXT FILE START =====
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

===== CONTEXT FILE END =====

Then create, in this order, under folder `pipelines/claimwise/`:
1. Orchestration `10_bronze_load`: seven SQL Script components, one per statement from the BRONZE SQL below, run in parallel, run verbatim. The CSVs are already in volume `/Volumes/claimwise/landing/raw/<table>/<table>.csv`.
2. Transformation pipelines for the 7 `stg_*` tables and the 4 `int_*` tables (schema `claimwise.silver`), and orchestration `20_silver` that runs stg_* in parallel, then int_* in parallel.
3. Transformation pipelines for the 13 gold dimensions/facts and the 6 `mtr_*` metric tables (schema `claimwise.gold`), and orchestration `30_gold` (dims/facts in parallel, then mtr_* in parallel).
4. Master orchestration `00_claimwise_daily` calling 10 -> 20 -> 30, failing fast.
5. Run `00_claimwise_daily` end to end, then run the row-count and KPI checks from the rules ("Expected results after a full run") and report the actual numbers.
Commit after each layer. Where the dbt spec uses Jinja, apply the translation table in the context file. Treat `{{ ref(x) }}` as the already-built table in `claimwise.silver` or `claimwise.gold`.

===== BRONZE SQL (run verbatim, one component per statement) =====
-- Bronze: load each landed CSV 1:1 into a typed Delta table. Full reload, idempotent.
-- This is the SQL the Matillion bronze orchestration pipeline executes (one SQL Script
-- component per table) so that Unity Catalog records volume -> bronze lineage.
CREATE OR REPLACE TABLE claimwise.bronze.users COMMENT 'All system actors: patients, doctors, staff, payers (source: Patient Management, MSSQL)' AS
SELECT CAST(id AS INT) AS id, userID, userType, name, CAST(dateOfBirth AS DATE) AS dateOfBirth,
       contactInfo, specialty, department, role
FROM read_files('/Volumes/claimwise/landing/raw/users/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.facilities COMMENT 'Healthcare facilities (source: Patient Management, MSSQL)' AS
SELECT CAST(id AS INT) AS id, facilityID, name, location, contactInfo
FROM read_files('/Volumes/claimwise/landing/raw/facilities/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.encounters COMMENT 'Patient encounters / visits (source: Patient Management, MSSQL)' AS
SELECT CAST(id AS INT) AS id, encounterID, CAST(patientID AS INT) AS patientID, CAST(doctorID AS INT) AS doctorID,
       CAST(facilityID AS INT) AS facilityID, CAST(date AS DATE) AS date, type, CAST(duration AS INT) AS duration, notes
FROM read_files('/Volumes/claimwise/landing/raw/encounters/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.health_plans COMMENT 'Insurance plans offered by payers (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, healthPlanID, planName, CAST(payerID AS INT) AS payerID
FROM read_files('/Volumes/claimwise/landing/raw/health_plans/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.claims COMMENT 'Medical claims and their lifecycle status (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, claimID, CAST(patientID AS INT) AS patientID, CAST(payerID AS INT) AS payerID, status,
       CAST(dateCreated AS DATE) AS dateCreated, CAST(dateUpdated AS DATE) AS dateUpdated, CAST(amount AS DOUBLE) AS amount
FROM read_files('/Volumes/claimwise/landing/raw/claims/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.activities COMMENT 'Claim lifecycle activities and events (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, activityID, CAST(claimID AS INT) AS claimID, CAST(activityDate AS DATE) AS activityDate,
       activityType, diagnosisCode, procedureCode, notes
FROM read_files('/Volumes/claimwise/landing/raw/activities/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.collections COMMENT 'Payment collections against claims (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, collectionID, CAST(claimID AS INT) AS claimID, CAST(date AS DATE) AS date,
       methodOfCollection, CAST(amountCollected AS DOUBLE) AS amountCollected, status
FROM read_files('/Volumes/claimwise/landing/raw/collections/', format => 'csv', header => true, inferColumnTypes => false)

===== END BRONZE SQL =====

===== TRANSFORMATION SPEC (dbt model SQL; rebuild each as a native transformation pipeline) =====

--- SPEC gold/admin/dim_staff.sql ---
-- models/gold/admin/dim_staff.sql
{{ config(materialized='table') }}

select
    staff_id,
    staff_code,
    staff_name,
    department,
    role,
    contactInfo as contact_info,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from {{ ref('int_staff') }}

--- SPEC gold/billing/dim_payer.sql ---
-- models/gold/billing/dim_payer.sql
{{ config(materialized='table') }}

select
    payer_id,
    payer_code,
    payer_name,
    contactInfo as contact_info,
    total_claims_received,
    total_claims_amount,
    avg_claim_amount,
    unique_patients,
    total_health_plans,
    plan_names,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from {{ ref('int_payers') }}

--- SPEC gold/billing/fct_claim_activities.sql ---
-- models/gold/billing/fct_claim_activities.sql
{{ config(materialized='table') }}

with activities as (
    select * from {{ ref('stg_activities') }}
),

claims as (
    select * from {{ ref('stg_claims') }}
)

select
    a.id as activity_id,
    a.activityID as activity_code,
    a.claimID as claim_key,
    c.patientID as patient_key,
    c.payerID as payer_key,
    a.activityDate as activity_date,
    a.activityType as activity_type,
    a.diagnosisCode,
    a.procedureCode,
    -- Metrics
    1 as activity_count,
    case when a.activityType = 'Appeal' then 1 else 0 end as is_appeal,
    case when a.activityType = 'Documentation Request' then 1 else 0 end as is_documentation_request
from activities a
left join claims c on a.claimID = c.id

--- SPEC gold/billing/fct_claims.sql ---
{{ config(materialized='table') }}

with claims as (
    select * from {{ ref('stg_claims') }}
),
patients as (
    select * from {{ ref('int_patients') }}
),
payers as (
    select * from {{ ref('int_payers') }}
)

select
    c.id as claim_id,
    c.claimID as claim_code,
    c.dateCreated as claim_date,
    c.patientID as patient_key,
    c.payerID as payer_key,
    c.status as claim_status,
    c.amount as claim_amount,
    -- Metrics
    1 as claim_count,
    case when c.status = 'Approved' then 1 else 0 end as approved_claim_flag,
    case when c.status = 'Denied' then 1 else 0 end as denied_claim_flag,
    p.total_encounters as patient_total_encounters,
    py.total_claims_received as payer_total_claims
from claims c
left join patients p on c.patientID = p.patient_id
left join payers py on c.payerID = py.payer_id

--- SPEC gold/billing/fct_collections.sql ---
-- models/gold/billing/fct_collections.sql
{{ config(materialized='table') }}

with collections as (
    select * from {{ ref('stg_collections') }}
),

claims as (
    select * from {{ ref('stg_claims') }}
)

select
    col.id as collection_id,
    col.collectionID as collection_code,
    col.claimID as claim_key,
    c.patientID as patient_key,
    c.payerID as payer_key,
    col.date as collection_date,
    col.methodOfCollection as collection_method,
    col.amountCollected as collected_amount,
    col.status as collection_status,
    -- Metrics
    1 as collection_count,
    case 
        when col.status = 'Completed' then 1 
        else 0 
    end as successful_collection_flag,
    col.amountCollected / NULLIF(c.amount, 0) as collection_rate
from collections col
left join claims c on col.claimID = c.id

--- SPEC gold/clinical/dim_diagnosis.sql ---
-- models/gold/clinical/dim_diagnosis.sql
{{ config(materialized='table') }}

with diagnoses as (
    select distinct 
        diagnosisCode,
        count(*) as usage_count
    from {{ ref('stg_activities') }}  -- Fixed reference
    where diagnosisCode is not null
    group by diagnosisCode
)

select
    diagnosisCode as diagnosis_id,
    diagnosisCode as diagnosis_code,  -- ICD code
    usage_count as total_claims_with_diagnosis,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from diagnoses

--- SPEC gold/clinical/dim_doctor.sql ---
-- models/gold/clinical/dim_diagnosis.sql
{{ config(materialized='table') }}

with diagnoses as (
    select distinct 
        diagnosisCode,
        count(*) as usage_count
    from {{ ref('stg_activities') }}
    where diagnosisCode is not null
    group by diagnosisCode
)

select
    diagnosisCode as diagnosis_id,
    diagnosisCode as diagnosis_code,  -- ICD code
    usage_count as total_claims_with_diagnosis,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from diagnoses

--- SPEC gold/clinical/dim_patient.sql ---
-- models/gold/clinical/dim_patient.sql
{{ config(materialized='table') }}

select
    patient_id,
    patient_code,
    patient_name,
    dateOfBirth,
    contactInfo,
    total_encounters,
    last_encounter_date,
    total_claims,
    total_claims_amount,
    last_claim_date
from {{ ref('int_patients') }}

--- SPEC gold/clinical/fct_encounters.sql ---
{{ config(materialized='table') }}

with encounters as (
    select * from {{ ref('stg_encounters') }}
),
patients as (
    select * from {{ ref('int_patients') }}
),
doctors as (
    select * from {{ ref('int_doctors') }}
)

select
    e.id as encounter_id,
    e.encounterID as encounter_code,
    e.date as encounter_date,
    e.patientID as patient_key,
    e.doctorID as doctor_key,
    e.facilityID as facility_key,
    e.type as encounter_type,
    e.duration as duration_minutes,
    -- Metrics
    1 as encounter_count,
    case when e.type = 'Emergency' then 1 else 0 end as emergency_visit_flag,
    p.total_claims as patient_total_claims,
    d.total_patients_seen as doctor_total_patients
from encounters e
left join patients p on e.patientID = p.patient_id
left join doctors d on e.doctorID = d.doctor_id

--- SPEC gold/core/dim_date.sql ---
with date_spine as (
    {{ dbt_date.get_date_dimension(
        start_date="2024-01-01",
        end_date="2026-12-31"
    ) }}
)
select
    date_day as date_id,
    date_day as full_date,
    {{ dbt_date.date_part('year', 'date_day') }} as year, -- Correct macro for extracting the year
    {{ dbt_date.date_part('month', 'date_day') }} as month_number,
    {{ dbt_date.month_name('date_day') }} as month_name, -- Extracts month name
    {{ dbt_date.date_part('quarter', 'date_day') }} as quarter,
    {{ dbt_date.day_of_week('date_day') }} as day_of_week,
    {{ dbt_date.day_name('date_day') }} as day_name, -- Extracts day name
    {{ dbt_date.iso_week_end('date_day') }} as is_weekend,
    {{ dbt_date.iso_week_start('date_day') }} as week_start_date,
    {{ dbt_date.week_end('date_day') }} as week_end_date
from date_spine

--- SPEC gold/core/dim_department.sql ---
-- models/gold/core/dim_department.sql
{{ config(materialized='table') }}

select distinct
    department as department_id,
    department as department_name,
    count(distinct id) as staff_count
from {{ ref('stg_users') }}
where userType = 'STAFF'
  and department is not null
group by department

--- SPEC gold/core/dim_facility.sql ---
-- models/gold/core/dim_facility.sql
{{ config(materialized='table') }}

with facilities as (
    select * from {{ ref('stg_facilities') }}
),

facility_metrics as (
    select 
        facilityID,
        count(distinct patientID) as total_patients_served,
        count(distinct doctorID) as total_doctors_practicing
    from {{ ref('stg_encounters') }}
    group by facilityID
)

select
    f.id as facility_id,
    f.facilityID as facility_code,
    f.name as facility_name,
    f.location as facility_location,
    f.contactInfo as contact_info,
    fm.total_patients_served,
    fm.total_doctors_practicing
from facilities f
left join facility_metrics fm on f.id = fm.facilityID

--- SPEC gold/core/dim_health_plan.sql ---
-- models/gold/core/dim_health_plan.sql
{{ config(materialized='table') }}

with health_plans as (
    select * from {{ ref('stg_health_plans') }}
),

plan_metrics as (
    select 
        hp.id as health_plan_id,
        count(distinct c.patientID) as enrolled_patients,
        sum(c.amount) as total_claims_amount
    from health_plans hp
    left join {{ ref('stg_claims') }} c on hp.payerID = c.payerID
    group by hp.id
)

select
    hp.id as health_plan_id,
    hp.healthPlanID as health_plan_code,
    hp.planName as plan_name,
    hp.payerID as payer_key,
    pm.enrolled_patients,
    pm.total_claims_amount,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from health_plans hp
left join plan_metrics pm on hp.id = pm.health_plan_id

--- SPEC gold/metrics/mtr_ar_aging.sql ---
-- Metric layer: open accounts receivable by payer and aging bucket.
-- Open AR = claim amount minus collections, for claims not denied.
{{ config(materialized='table') }}

with collected_per_claim as (
    select claim_key, sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by claim_key
),

open_claims as (
    select
        f.payer_key,
        f.claim_amount - coalesce(c.collected_amount, 0) as open_amount,
        {{ dbt.datediff("f.claim_date", "current_date", "day") }} as age_days
    from {{ ref('fct_claims') }} f
    left join collected_per_claim c on f.claim_id = c.claim_key
    where f.claim_status != 'Denied'
      and f.claim_amount - coalesce(c.collected_amount, 0) > 0
)

select
    p.payer_name,
    case
        when o.age_days <= 30 then '0-30'
        when o.age_days <= 60 then '31-60'
        when o.age_days <= 90 then '61-90'
        else '90+'
    end as aging_bucket,
    case
        when o.age_days <= 30 then 1
        when o.age_days <= 60 then 2
        when o.age_days <= 90 then 3
        else 4
    end as bucket_order,
    count(*) as open_claim_count,
    round(sum(o.open_amount), 2) as open_ar_amount
from open_claims o
inner join {{ ref('dim_payer') }} p on o.payer_key = p.payer_id
group by 1, 2, 3
order by p.payer_name, bucket_order

--- SPEC gold/metrics/mtr_claims_funnel.sql ---
-- Metric layer: claim lifecycle funnel by status.
{{ config(materialized='table') }}

select
    claim_status,
    count(*) as claim_count,
    round(sum(claim_amount), 2) as total_amount,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as pct_of_claims
from {{ ref('fct_claims') }}
group by claim_status
order by claim_count desc

--- SPEC gold/metrics/mtr_department_activity.sql ---
-- Metric layer: encounter activity by medical specialty. Volumes only —
-- claims are not linked to encounters in the source schema, so revenue is
-- not attributed to specialties.
{{ config(materialized='table') }}

select
    d.specialty,
    count(*) as encounter_count,
    count(distinct e.patient_key) as unique_patients,
    count(distinct e.doctor_key) as active_doctors,
    round(avg(e.duration_minutes), 1) as avg_duration_minutes,
    sum(e.emergency_visit_flag) as emergency_visits
from {{ ref('fct_encounters') }} e
inner join {{ ref('int_doctors') }} d on e.doctor_key = d.doctor_id
group by d.specialty
order by encounter_count desc

--- SPEC gold/metrics/mtr_executive_summary.sql ---
-- Metric layer: single-row executive KPI summary. Every headline number on
-- the dashboard comes from here — defined once, consumed everywhere.
{{ config(materialized='table') }}

with collected_per_claim as (
    select claim_key, sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by claim_key
),

claims as (
    select
        sum(f.claim_amount) as gross_billed,
        sum(coalesce(c.collected_amount, 0)) as total_collected,
        count(*) as claim_count,
        sum(f.denied_claim_flag) as denied_count,
        sum(case
            when f.claim_status != 'Denied'
             and f.claim_amount - coalesce(c.collected_amount, 0) > 0
            then f.claim_amount - coalesce(c.collected_amount, 0)
            else 0
        end) as open_ar
    from {{ ref('fct_claims') }} f
    left join collected_per_claim c on f.claim_id = c.claim_key
),

cycle as (
    select round(avg({{ dbt.datediff("dateCreated", "dateUpdated", "day") }}), 1) as avg_cycle_days
    from {{ ref('stg_claims') }}
),

encounters as (
    select count(*) as encounter_count
    from {{ ref('fct_encounters') }}
)

select
    round(cl.gross_billed, 2) as gross_billed,
    round(cl.total_collected, 2) as total_collected,
    round(100.0 * cl.total_collected / nullif(cl.gross_billed, 0), 2) as collection_rate_pct,
    round(100.0 * cl.denied_count / nullif(cl.claim_count, 0), 2) as denial_rate_pct,
    round(cl.open_ar, 2) as open_ar,
    cy.avg_cycle_days,
    cl.claim_count,
    e.encounter_count
from claims cl
cross join cycle cy
cross join encounters e

--- SPEC gold/metrics/mtr_payer_scorecard.sql ---
-- Metric layer: one row per payer with the full billing scorecard.
{{ config(materialized='table') }}

with collected_per_claim as (
    select claim_key, sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by claim_key
),

claims as (
    select
        f.payer_key,
        sum(f.claim_amount) as billed_amount,
        sum(coalesce(c.collected_amount, 0)) as collected_amount,
        count(*) as claim_count,
        sum(f.denied_claim_flag) as denied_count,
        round(avg(f.claim_amount), 2) as avg_claim_amount,
        sum(case
            when f.claim_status != 'Denied'
             and f.claim_amount - coalesce(c.collected_amount, 0) > 0
            then f.claim_amount - coalesce(c.collected_amount, 0)
            else 0
        end) as open_ar
    from {{ ref('fct_claims') }} f
    left join collected_per_claim c on f.claim_id = c.claim_key
    group by f.payer_key
)

select
    p.payer_name,
    c.billed_amount,
    c.collected_amount,
    round(100.0 * c.collected_amount / nullif(c.billed_amount, 0), 2) as collection_rate_pct,
    round(100.0 * c.denied_count / nullif(c.claim_count, 0), 2) as denial_rate_pct,
    c.open_ar,
    c.claim_count,
    c.avg_claim_amount
from claims c
inner join {{ ref('dim_payer') }} p on c.payer_key = p.payer_id
order by c.billed_amount desc

--- SPEC gold/metrics/mtr_revenue_monthly.sql ---
-- Metric layer: monthly billed vs collected. Consumers read these columns
-- as-is; no re-aggregation downstream.
{{ config(materialized='table') }}

with billed as (
    select
        {{ dbt.date_trunc("month", "claim_date") }} as month,
        sum(claim_amount) as billed_amount,
        count(*) as claim_count,
        sum(denied_claim_flag) as denied_count
    from {{ ref('fct_claims') }}
    group by 1
),

collected as (
    select
        {{ dbt.date_trunc("month", "collection_date") }} as month,
        sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by 1
)

select
    cast(coalesce(b.month, c.month) as date) as month,
    coalesce(b.billed_amount, 0) as billed_amount,
    coalesce(c.collected_amount, 0) as collected_amount,
    round(100.0 * coalesce(c.collected_amount, 0) / nullif(b.billed_amount, 0), 2) as collection_rate_pct,
    coalesce(b.claim_count, 0) as claim_count,
    coalesce(b.denied_count, 0) as denied_count
from billed b
full outer join collected c on b.month = c.month
order by 1

--- SPEC silver/intermediate/users/int_doctors.sql ---
{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
),

doctor_encounters as (
    select 
        doctorID, -- matches silver model case
        count(*) as total_patients_seen,
        count(distinct patientID) as unique_patients_seen,
        max(date) as last_encounter_date
    from {{ ref('stg_encounters') }}
    group by doctorID
),

doctor_facilities as (
    select 
        e.doctorID,
        count(distinct e.facilityID) as facilities_practiced_in,
        {{ dbt.listagg(measure="distinct f.name", delimiter_text="', '") }} as facility_names
    from {{ ref('stg_encounters') }} e
    join {{ ref('stg_facilities') }} f on e.facilityID = f.id
    group by e.doctorID
)

select distinct
    s.id as doctor_id,
    s.userID as doctor_code,
    s.name as doctor_name,
    s.specialty,
    s.contactInfo,
    de.total_patients_seen,
    de.unique_patients_seen,
    de.last_encounter_date,
    df.facilities_practiced_in,
    df.facility_names
from source s
left join doctor_encounters de on s.id = de.doctorID
left join doctor_facilities df on s.id = df.doctorID
where s.userType = 'DOCTOR'

--- SPEC silver/intermediate/users/int_patients.sql ---
{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
),

patient_encounters as (
    select 
        patientID,
        count(*) as total_encounters,
        max(date) as last_encounter_date
    from {{ ref('stg_encounters') }}
    group by patientID
),

patient_claims as (
    select 
        patientID,
        count(*) as total_claims,
        sum(amount) as total_claims_amount,
        max(dateCreated) as last_claim_date
    from {{ ref('stg_claims') }}
    group by patientID
)

select distinct
    s.id as patient_id,
    s.userID as patient_code,
    s.name as patient_name,
    s.dateOfBirth,
    s.contactInfo,
    coalesce(pe.total_encounters, 0) as total_encounters,
    pe.last_encounter_date,
    coalesce(pc.total_claims, 0) as total_claims,
    coalesce(pc.total_claims_amount, 0) as total_claims_amount,
    pc.last_claim_date
from source s
left join patient_encounters pe on s.id = pe.patientID
left join patient_claims pc on s.id = pc.patientID
where s.userType = 'PATIENT'

--- SPEC silver/intermediate/users/int_payers.sql ---
{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
),

payer_claims as (
    select 
        payerID,
        count(*) as total_claims_received,
        sum(amount) as total_claims_amount,
        avg(amount) as avg_claim_amount,
        count(distinct patientID) as unique_patients
    from {{ ref('stg_claims') }}
    group by payerID
),

payer_health_plans as (
    select 
        payerID,
        count(*) as total_health_plans,
        {{ dbt.listagg(measure='planName', delimiter_text="', '") }} as plan_names
    from {{ ref('stg_health_plans') }}
    group by payerID
)

select distinct
    s.id as payer_id,
    s.userID as payer_code,
    s.name as payer_name,
    s.contactInfo,
    pc.total_claims_received,
    pc.total_claims_amount,
    pc.avg_claim_amount,
    pc.unique_patients,
    hp.total_health_plans,
    hp.plan_names
from source s
left join payer_claims pc on s.id = pc.payerID
left join payer_health_plans hp on s.id = hp.payerID
where s.userType = 'PAYER'

--- SPEC silver/intermediate/users/int_staff.sql ---
{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
)

select distinct
    id as staff_id,
    userID as staff_code,
    name as staff_name,
    department,
    role,
    contactInfo
from source
where userType = 'STAFF'

--- SPEC silver/stg_activities.sql ---
with source as (

    select * from {{ source('bronze', 'activities') }}

),

renamed as (

    select
        id,
        activityID,
        claimID,
        activityDate,
        activityType,
        diagnosisCode,
        procedureCode,
        notes

    from source

)

select * from renamed

--- SPEC silver/stg_claims.sql ---
with source as (

    select * from {{ source('bronze', 'claims') }}

),

renamed as (

    select
        id,
        claimID,
        patientID,
        payerID,
        status,
        dateCreated,
        dateUpdated,
        amount

    from source

)

select * from renamed

--- SPEC silver/stg_collections.sql ---
with source as (

    select * from {{ source('bronze', 'collections') }}

),

renamed as (

    select
        id,
        collectionID,
        claimID,
        date,
        methodOfCollection,
        amountCollected,
        status

    from source

)

select * from renamed

--- SPEC silver/stg_encounters.sql ---
with source as (

    select * from {{ source('bronze', 'encounters') }}

),

renamed as (

    select
        id,
        encounterID,
        patientID,
        doctorID,
        facilityID,
        date,
        type,
        duration,
        notes

    from source

)

select * from renamed

--- SPEC silver/stg_facilities.sql ---
with source as (

    select * from {{ source('bronze', 'facilities') }}

),

renamed as (

    select
        id,
        facilityID,
        name,
        location,
        contactInfo

    from source

)

select * from renamed

--- SPEC silver/stg_health_plans.sql ---
with source as (

    select * from {{ source('bronze', 'health_plans') }}

),

renamed as (

    select
        id,
        healthPlanID,
        planName,
        payerID

    from source

)

select * from renamed

--- SPEC silver/stg_users.sql ---
with source as (

    select * from {{ source('bronze', 'users') }}

),

renamed as (

    select
        id,
        userID,
        userType,
        name,
        dateOfBirth,
        contactInfo,
        specialty,
        department,
        role

    from source

)

select * from renamed

===== END SPEC =====

===== DATA QUALITY SPEC (silver column tests to express as Matillion tests) =====
version: 2

# Daily validation checks from the data-quality framework:
# uniqueness constraints, not-null checks, and code validations.

models:
  - name: stg_users
    columns:
      - name: id
        tests: [unique, not_null]
      - name: userID
        tests: [unique, not_null]
      - name: userType
        tests:
          - not_null
          - accepted_values:
              values: ['PATIENT', 'DOCTOR', 'STAFF', 'PAYER']

  - name: stg_claims
    columns:
      - name: id
        tests: [unique, not_null]
      - name: claimID
        tests: [unique, not_null]
      - name: amount
        tests: [not_null]
      - name: status
        tests:
          - not_null
          - accepted_values:
              values: ['Submitted', 'In Review', 'Approved', 'Denied', 'Appealed']

  - name: stg_collections
    columns:
      - name: id
        tests: [unique, not_null]
      - name: collectionID
        tests: [unique, not_null]
      - name: methodOfCollection
        tests:
          - accepted_values:
              values: ['Cash', 'Credit Card', 'Bank Transfer', 'Check', 'Electronic Payment']
      - name: status
        tests:
          - accepted_values:
              values: ['Processed', 'Pending', 'Completed', 'Failed']

  - name: stg_encounters
    columns:
      - name: id
        tests: [unique, not_null]
      - name: encounterID
        tests: [unique, not_null]
      - name: type
        tests:
          - accepted_values:
              values: ['Initial Visit', 'Follow-up', 'Emergency', 'Routine Checkup', 'Specialist Consultation']

  - name: stg_activities
    columns:
      - name: id
        tests: [unique, not_null]
      - name: activityID
        tests: [unique, not_null]
      - name: activityType
        tests:
          - accepted_values:
              values: ['Submission', 'Review', 'Documentation Request', 'Appeal', 'Payment Processing']

  - name: stg_facilities
    columns:
      - name: id
        tests: [unique, not_null]
      - name: facilityID
        tests: [unique, not_null]

  - name: stg_health_plans
    columns:
      - name: id
        tests: [unique, not_null]
      - name: healthPlanID
        tests: [unique, not_null]

===== END DATA QUALITY SPEC =====

