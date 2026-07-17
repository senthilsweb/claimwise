-- models/mart/billing/dim_payer.sql
{{ config(materialized='table') }}

select
    payer_id,
    payer_code,
    payer_name,
    "contactInfo" as contact_info,
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