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
