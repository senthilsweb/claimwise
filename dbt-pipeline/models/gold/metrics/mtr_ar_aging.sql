-- Metric layer: open accounts receivable by payer and aging bucket.
-- Open AR = claim amount minus collections, for claims not denied.
{{ config(materialized='table') }}

with collected_per_claim as (
    select claim_key, sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by claim_key
),

open_claims as (
    select
        f.payer_key,
        f.claim_amount - coalesce(c.collected_amount, 0) as open_amount,
        {{ dbt.datediff("f.claim_date", "current_date", "day") }} as age_days
    from {{ ref('fct_claims') }} f
    left join collected_per_claim c on f.claim_id = c.claim_key
    where f.claim_status != 'Denied'
      and f.claim_amount - coalesce(c.collected_amount, 0) > 0
)

select
    p.payer_name,
    case
        when o.age_days <= 30 then '0-30'
        when o.age_days <= 60 then '31-60'
        when o.age_days <= 90 then '61-90'
        else '90+'
    end as aging_bucket,
    case
        when o.age_days <= 30 then 1
        when o.age_days <= 60 then 2
        when o.age_days <= 90 then 3
        else 4
    end as bucket_order,
    count(*) as open_claim_count,
    round(sum(o.open_amount), 2) as open_ar_amount
from open_claims o
inner join {{ ref('dim_payer') }} p on o.payer_key = p.payer_id
group by 1, 2, 3
order by p.payer_name, bucket_order
