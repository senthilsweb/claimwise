-- Invariant (weekly · provider-service matching): every doctor must have a
-- specialty, and every encounter must be performed by a DOCTOR-type user.

select 'doctor_missing_specialty' as issue, u.id as key_value
from {{ ref('stg_users') }} u
where u.userType = 'DOCTOR'
  and (u.specialty is null or trim(u.specialty) = '')

union all

select 'encounter_provider_not_doctor' as issue, e.id as key_value
from {{ ref('stg_encounters') }} e
inner join {{ ref('stg_users') }} u on e.doctorID = u.id
where u.userType != 'DOCTOR'
