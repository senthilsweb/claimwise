-- models/mart/admin/dim_staff.sql
{{ config(materialized='table') }}

select
    staff_id,
    staff_code,
    staff_name,
    "department",
    "role",
    "contactInfo" as contact_info,
    current_timestamp as valid_from,
    cast(null as timestamp) as valid_to,
    True as is_current
from {{ ref('int_staff') }}