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
    c."id" as claim_id,
    c."claimID" as claim_code,
    c."dateCreated" as claim_date,
    c."patientID" as patient_key,
    c."payerID" as payer_key,
    c."status" as claim_status,
    c."amount" as claim_amount,
    -- Metrics
    1 as claim_count,
    case when c."status" = 'Approved' then 1 else 0 end as approved_claim_flag,
    case when c."status" = 'Denied' then 1 else 0 end as denied_claim_flag,
    p.total_encounters as patient_total_encounters,
    py.total_claims_received as payer_total_claims
from claims c
left join patients p on c."patientID" = p.patient_id
left join payers py on c."payerID" = py.payer_id