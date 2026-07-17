with source as (

    select * from {{ source('raw', 'encounters') }}

),

renamed as (

    select
        "id",
        "encounterID",
        "patientID",
        "doctorID",
        "facilityID",
        "date",
        "type",
        "duration",
        "notes"

    from source

)

select * from renamed

