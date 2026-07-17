-- Invariant (weekly · cross-reference validation): every foreign key must
-- resolve to its parent — claims to patients/payers, activities and
-- collections to claims, encounters to patients/doctors/facilities,
-- health plans to payers.

with users as (
    select id, userType from {{ ref('stg_users') }}
)

select 'claims.patientID' as relationship, c.id as key_value
from {{ ref('stg_claims') }} c
left join users u on c.patientID = u.id and u.userType = 'PATIENT'
where u.id is null

union all

select 'claims.payerID' as relationship, c.id as key_value
from {{ ref('stg_claims') }} c
left join users u on c.payerID = u.id and u.userType = 'PAYER'
where u.id is null

union all

select 'activities.claimID' as relationship, a.id as key_value
from {{ ref('stg_activities') }} a
left join {{ ref('stg_claims') }} c on a.claimID = c.id
where c.id is null

union all

select 'collections.claimID' as relationship, col.id as key_value
from {{ ref('stg_collections') }} col
left join {{ ref('stg_claims') }} c on col.claimID = c.id
where c.id is null

union all

select 'encounters.patientID' as relationship, e.id as key_value
from {{ ref('stg_encounters') }} e
left join users u on e.patientID = u.id and u.userType = 'PATIENT'
where u.id is null

union all

select 'encounters.doctorID' as relationship, e.id as key_value
from {{ ref('stg_encounters') }} e
left join users u on e.doctorID = u.id and u.userType = 'DOCTOR'
where u.id is null

union all

select 'encounters.facilityID' as relationship, e.id as key_value
from {{ ref('stg_encounters') }} e
left join {{ ref('stg_facilities') }} f on e.facilityID = f.id
where f.id is null

union all

select 'health_plans.payerID' as relationship, hp.id as key_value
from {{ ref('stg_health_plans') }} hp
left join users u on hp.payerID = u.id and u.userType = 'PAYER'
where u.id is null
