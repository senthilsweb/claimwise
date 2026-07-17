with source as (

    select * from {{ source('raw', 'activities') }}

),

renamed as (

    select
        "id",
        "activityID",
        "claimID",
        "activityDate",
        "activityType",
        "diagnosisCode",
        "procedureCode",
        "notes"

    from source

)

select * from renamed

