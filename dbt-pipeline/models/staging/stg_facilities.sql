with source as (

    select * from {{ source('raw', 'facilities') }}

),

renamed as (

    select
        "id",
        "facilityID",
        "name",
        "location",
        "contactInfo"

    from source

)

select * from renamed

