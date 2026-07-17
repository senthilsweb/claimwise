-- models/mart/billing/fct_collections.sql
{{ config(materialized='table') }}

with collections as (
    select * from {{ ref('stg_collections') }}
),

claims as (
    select * from {{ ref('stg_claims') }}
)

select
    col."id" as collection_id,
    col."collectionID" as collection_code,
    col."claimID" as claim_key,
    c."patientID" as patient_key,
    c."payerID" as payer_key,
    col."date" as collection_date,
    col."methodOfCollection" as collection_method,
    col."amountCollected" as collected_amount,
    col."status" as collection_status,
    -- Metrics
    1 as collection_count,
    case 
        when col."status" = 'Completed' then 1 
        else 0 
    end as successful_collection_flag,
    col."amountCollected" / NULLIF(c."amount", 0) as collection_rate
from collections col
left join claims c on col."claimID" = c."id"