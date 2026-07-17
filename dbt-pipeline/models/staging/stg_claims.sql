with source as (

    select * from {{ source('raw', 'claims') }}

),

renamed as (

    select
        "id",
        "claimID",
        "patientID",
        "payerID",
        "status",
        "dateCreated",
        "dateUpdated",
        "amount"

    from source

)

select * from renamed

