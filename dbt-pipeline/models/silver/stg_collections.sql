with source as (

    select * from {{ source('bronze', 'collections') }}

),

renamed as (

    select
        id,
        collectionID,
        claimID,
        date,
        methodOfCollection,
        amountCollected,
        status

    from source

)

select * from renamed

