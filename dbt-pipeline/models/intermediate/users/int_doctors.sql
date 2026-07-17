{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
),

doctor_encounters as (
    select 
        "doctorID", -- matches staging model case
        count(*) as total_patients_seen,
        count(distinct "patientID") as unique_patients_seen,
        max("date") as last_encounter_date
    from {{ ref('stg_encounters') }}
    group by "doctorID"
),

doctor_facilities as (
    select 
        e."doctorID",
        count(distinct e."facilityID") as facilities_practiced_in,
        {{ dbt.listagg(measure="distinct f.name", delimiter_text="', '") }} as facility_names
    from {{ ref('stg_encounters') }} e
    join {{ ref('stg_facilities') }} f on e."facilityID" = f."id"
    group by e."doctorID"
)

select distinct
    s."id" as doctor_id,
    s."userID" as doctor_code,
    s."name" as doctor_name,
    s."specialty",
    s."contactInfo",
    de.total_patients_seen,
    de.unique_patients_seen,
    de.last_encounter_date,
    df.facilities_practiced_in,
    df.facility_names
from source s
left join doctor_encounters de on s."id" = de."doctorID"
left join doctor_facilities df on s."id" = df."doctorID"
where s."userType" = 'DOCTOR'