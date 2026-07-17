with source as (

    select * from {{ source('raw', 'collections') }}

),

renamed as (

    select
        "id",
        "collectionID",
        "claimID",
        "date",
        "methodOfCollection",
        "amountCollected",
        "status"

    from source

)

select * from renamed

