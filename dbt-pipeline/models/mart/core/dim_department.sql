-- models/mart/core/dim_department.sql
{{ config(materialized='table') }}

select distinct
    "department" as department_id,
    "department" as department_name,
    count(distinct "id") as staff_count
from {{ ref('stg_users') }}
where "userType" = 'STAFF'
  and "department" is not null
group by "department"