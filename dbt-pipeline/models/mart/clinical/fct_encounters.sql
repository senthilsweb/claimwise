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
    e."id" as encounter_id,
    e."encounterID" as encounter_code,
    e."date" as encounter_date,
    e."patientID" as patient_key,
    e."doctorID" as doctor_key,
    e."facilityID" as facility_key,
    e."type" as encounter_type,
    e."duration" as duration_minutes,
    -- Metrics
    1 as encounter_count,
    case when e."type" = 'Emergency' then 1 else 0 end as emergency_visit_flag,
    p.total_claims as patient_total_claims,
    d.total_patients_seen as doctor_total_patients
from encounters e
left join patients p on e."patientID" = p.patient_id
left join doctors d on e."doctorID" = d.doctor_id