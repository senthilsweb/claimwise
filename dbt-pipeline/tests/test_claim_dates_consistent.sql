-- Invariant (daily · date validation): claims cannot be created after their
-- last update or dated in the future, and claim activities must fall inside
-- the claim's created/updated window.

select 'claim_dates_inverted_or_future' as issue, c.id as key_value
from {{ ref('stg_claims') }} c
where c.dateCreated > c.dateUpdated
   or c.dateCreated > current_date

union all

select 'activity_outside_claim_window' as issue, a.id as key_value
from {{ ref('stg_activities') }} a
inner join {{ ref('stg_claims') }} c on a.claimID = c.id
where a.activityDate < c.dateCreated
   or a.activityDate > c.dateUpdated
