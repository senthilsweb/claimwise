-- Invariant (daily · format validation): business identifiers must carry
-- their domain prefix (CLM, COL, ENC, ACT, FAC, HP; DR/PT/STF/PAY by user type)
-- and diagnosis/procedure codes must be ICD-/CPT- prefixed.

select 'claims' as entity, claimID as key_value
from {{ ref('stg_claims') }}
where claimID not like 'CLM%'

union all

select 'collections' as entity, collectionID as key_value
from {{ ref('stg_collections') }}
where collectionID not like 'COL%'

union all

select 'encounters' as entity, encounterID as key_value
from {{ ref('stg_encounters') }}
where encounterID not like 'ENC%'

union all

select 'activities' as entity, activityID as key_value
from {{ ref('stg_activities') }}
where activityID not like 'ACT%'

union all

select 'facilities' as entity, facilityID as key_value
from {{ ref('stg_facilities') }}
where facilityID not like 'FAC%'

union all

select 'health_plans' as entity, healthPlanID as key_value
from {{ ref('stg_health_plans') }}
where healthPlanID not like 'HP%'

union all

select 'users' as entity, userID as key_value
from {{ ref('stg_users') }}
where (userType = 'DOCTOR' and userID not like 'DR%')
   or (userType = 'PATIENT' and userID not like 'PT%')
   or (userType = 'STAFF' and userID not like 'STF%')
   or (userType = 'PAYER' and userID not like 'PAY%')

union all

select 'activity_codes' as entity, activityID as key_value
from {{ ref('stg_activities') }}
where (diagnosisCode is not null and diagnosisCode not like 'ICD-%')
   or (procedureCode is not null and procedureCode not like 'CPT-%')
