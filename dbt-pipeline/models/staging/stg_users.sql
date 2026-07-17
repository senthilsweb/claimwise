with source as (

    select * from {{ source('raw', 'users') }}

),

renamed as (

    select
        "id",
        "userID",
        "userType",
        "name",
        "dateOfBirth",
        "contactInfo",
        "specialty",
        "department",
        "role"

    from source

)

select * from renamed

