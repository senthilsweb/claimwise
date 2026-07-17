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