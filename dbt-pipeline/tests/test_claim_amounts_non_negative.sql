-- Invariant: claim_amount in fct_claims must never be negative
select
    claim_id,
    claim_code,
    claim_amount
from {{ ref('fct_claims') }}
where claim_amount < 0
