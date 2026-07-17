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