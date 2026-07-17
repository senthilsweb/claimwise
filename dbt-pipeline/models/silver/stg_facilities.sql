with source as (

    select * from {{ source('bronze', 'facilities') }}

),

renamed as (

    select
        id,
        facilityID,
        name,
        location,
        contactInfo

    from source

)

select * from renamed

