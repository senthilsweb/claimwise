-- models/mart/core/dim_facility.sql
{{ config(materialized='table') }}

with facilities as (
    select * from {{ ref('stg_facilities') }}
),

facility_metrics as (
    select 
        "facilityID",
        count(distinct "patientID") as total_patients_served,
        count(distinct "doctorID") as total_doctors_practicing
    from {{ ref('stg_encounters') }}
    group by "facilityID"
)

select
    f."id" as facility_id,
    f."facilityID" as facility_code,
    f."name" as facility_name,
    f."location" as facility_location,
    f."contactInfo" as contact_info,
    fm.total_patients_served,
    fm.total_doctors_practicing
from facilities f
left join facility_metrics fm on f."id" = fm."facilityID"