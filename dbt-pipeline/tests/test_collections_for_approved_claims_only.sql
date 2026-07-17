-- Invariant (weekly · payment reconciliation): payments may only be
-- collected against approved claims.

select col.id as collection_id, c.id as claim_id, c.status
from {{ ref('stg_collections') }} col
inner join {{ ref('stg_claims') }} c on col.claimID = c.id
where c.status != 'Approved'
