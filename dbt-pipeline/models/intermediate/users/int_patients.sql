{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
),

patient_encounters as (
    select 
        "patientID",
        count(*) as total_encounters,
        max("date") as last_encounter_date
    from {{ ref('stg_encounters') }}
    group by "patientID"
),

patient_claims as (
    select 
        "patientID",
        count(*) as total_claims,
        sum("amount") as total_claims_amount,
        max("dateCreated") as last_claim_date
    from {{ ref('stg_claims') }}
    group by "patientID"
)

select distinct
    s."id" as patient_id,
    s."userID" as patient_code,
    s."name" as patient_name,
    s."dateOfBirth",
    s."contactInfo",
    coalesce(pe.total_encounters, 0) as total_encounters,
    pe.last_encounter_date,
    coalesce(pc.total_claims, 0) as total_claims,
    coalesce(pc.total_claims_amount, 0) as total_claims_amount,
    pc.last_claim_date
from source s
left join patient_encounters pe on s."id" = pe."patientID"
left join patient_claims pc on s."id" = pc."patientID"
where s."userType" = 'PATIENT'