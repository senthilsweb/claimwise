-- Patient encounter analysis
with patient_metrics as (
    select 
        dp.patient_id,
        dp.patient_name,
        count(fe.encounter_id) as total_encounters,
        sum(fe.emergency_visit_flag) as emergency_visits,
        avg(fe.duration_minutes) as avg_visit_duration
    from {{ ref('dim_patient') }} dp
    left join {{ ref('fct_encounters') }} fe 
        on dp.patient_id = fe.patient_key
    group by 1, 2
)

select * from patient_metrics
where total_encounters > 5
order by emergency_visits desc;

-- Claims analysis by payer
select 
    dp.payer_name,
    count(fc.claim_id) as total_claims,
    sum(fc.claim_amount) as total_claim_amount,
    avg(fc.claim_amount) as avg_claim_amount,
    sum(fc.approved_claim_flag) as approved_claims,
    sum(fc.denied_claim_flag) as denied_claims
from {{ ref('dim_payer') }} dp
join {{ ref('fct_claims') }} fc 
    on dp.payer_id = fc.payer_key
group by 1
order by total_claim_amount desc;