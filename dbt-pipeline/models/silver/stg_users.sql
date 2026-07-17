with source as (

    select * from {{ source('bronze', 'users') }}

),

renamed as (

    select
        id,
        userID,
        userType,
        name,
        dateOfBirth,
        contactInfo,
        specialty,
        department,
        role

    from source

)

select * from renamed

