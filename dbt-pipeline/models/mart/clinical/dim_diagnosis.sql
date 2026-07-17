-- models/mart/clinical/dim_diagnosis.sql
{{ config(materialized='table') }}

with diagnoses as (
    select distinct 
        "diagnosisCode",
        count(*) as usage_count
    from {{ ref('stg_activities') }}  -- Fixed reference
    where "diagnosisCode" is not null
    group by "diagnosisCode"
)

select
    "diagnosisCode" as diagnosis_id,
    "diagnosisCode" as diagnosis_code,  -- ICD code
    usage_count as total_claims_with_diagnosis,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from diagnoses