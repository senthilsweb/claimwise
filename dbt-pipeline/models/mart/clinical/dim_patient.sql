-- models/mart/clinical/dim_patient.sql
{{ config(materialized='table') }}

select
    patient_id,
    patient_code,
    patient_name,
    "dateOfBirth",
    "contactInfo",
    total_encounters,
    last_encounter_date,
    total_claims,
    total_claims_amount,
    last_claim_date
from {{ ref('int_patients') }}