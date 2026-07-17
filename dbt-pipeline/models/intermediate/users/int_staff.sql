{{ config(materialized='view', bind=False) }}

with source as (
    select * from {{ ref('stg_users') }}
)

select distinct
    "id" as staff_id,
    "userID" as staff_code,
    "name" as staff_name,
    "department",
    "role",
    "contactInfo"
from source
where "userType" = 'STAFF'