-- Invariant (weekly · documentation completeness): every claim must have at
-- least one activity, and Documentation Request activities must carry notes.

select 'claim_without_activities' as issue, c.id as key_value
from {{ ref('stg_claims') }} c
left join {{ ref('stg_activities') }} a on c.id = a.claimID
group by c.id
having count(a.id) = 0

union all

select 'documentation_request_without_notes' as issue, a.id as key_value
from {{ ref('stg_activities') }} a
where a.activityType = 'Documentation Request'
  and (a.notes is null or trim(a.notes) = '')
