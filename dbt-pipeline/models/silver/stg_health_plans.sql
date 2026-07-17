with source as (

    select * from {{ source('bronze', 'health_plans') }}

),

renamed as (

    select
        id,
        healthPlanID,
        planName,
        payerID

    from source

)

select * from renamed

