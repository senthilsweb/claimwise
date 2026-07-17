-- models/mart/billing/fct_claim_activities.sql
{{ config(materialized='table') }}

with activities as (
    select * from {{ ref('stg_activities') }}
),

claims as (
    select * from {{ ref('stg_claims') }}
)

select
    a."id" as activity_id,
    a."activityID" as activity_code,
    a."claimID" as claim_key,
    c."patientID" as patient_key,
    c."payerID" as payer_key,
    a."activityDate" as activity_date,
    a."activityType" as activity_type,
    a."diagnosisCode",
    a."procedureCode",
    -- Metrics
    1 as activity_count,
    case when a."activityType" = 'Appeal' then 1 else 0 end as is_appeal,
    case when a."activityType" = 'Documentation Request' then 1 else 0 end as is_documentation_request
from activities a
left join claims c on a."claimID" = c."id"