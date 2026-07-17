-- Invariant: total collected per claim in fct_collections must not exceed the claim_amount in fct_claims
select
    col.claim_key,
    sum(col.collected_amount) as total_collected,
    max(cl.claim_amount) as claim_amount
from {{ ref('fct_collections') }} col
inner join {{ ref('fct_claims') }} cl
    on col.claim_key = cl.claim_id
group by col.claim_key
having sum(col.collected_amount) > max(cl.claim_amount)
