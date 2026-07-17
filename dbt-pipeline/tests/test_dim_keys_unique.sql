-- Invariant: primary keys of dim_patient and dim_facility must be unique
select 'dim_patient' as dim_name, patient_id as key_value, count(*) as row_count
from {{ ref('dim_patient') }}
group by patient_id
having count(*) > 1

union all

select 'dim_facility' as dim_name, facility_id as key_value, count(*) as row_count
from {{ ref('dim_facility') }}
group by facility_id
having count(*) > 1
