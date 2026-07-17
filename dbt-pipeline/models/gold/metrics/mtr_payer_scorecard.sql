-- Metric layer: one row per payer with the full billing scorecard.
{{ config(materialized='table') }}

with collected_per_claim as (
    select claim_key, sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by claim_key
),

claims as (
    select
        f.payer_key,
        sum(f.claim_amount) as billed_amount,
        sum(coalesce(c.collected_amount, 0)) as collected_amount,
        count(*) as claim_count,
        sum(f.denied_claim_flag) as denied_count,
        round(avg(f.claim_amount), 2) as avg_claim_amount,
        sum(case
            when f.claim_status != 'Denied'
             and f.claim_amount - coalesce(c.collected_amount, 0) > 0
            then f.claim_amount - coalesce(c.collected_amount, 0)
            else 0
        end) as open_ar
    from {{ ref('fct_claims') }} f
    left join collected_per_claim c on f.claim_id = c.claim_key
    group by f.payer_key
)

select
    p.payer_name,
    c.billed_amount,
    c.collected_amount,
    round(100.0 * c.collected_amount / nullif(c.billed_amount, 0), 2) as collection_rate_pct,
    round(100.0 * c.denied_count / nullif(c.claim_count, 0), 2) as denial_rate_pct,
    c.open_ar,
    c.claim_count,
    c.avg_claim_amount
from claims c
inner join {{ ref('dim_payer') }} p on c.payer_key = p.payer_id
order by c.billed_amount desc
