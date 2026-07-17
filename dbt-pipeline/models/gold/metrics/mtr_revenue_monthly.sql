-- Metric layer: monthly billed vs collected. Consumers read these columns
-- as-is; no re-aggregation downstream.
{{ config(materialized='table') }}

with billed as (
    select
        {{ dbt.date_trunc("month", "claim_date") }} as month,
        sum(claim_amount) as billed_amount,
        count(*) as claim_count,
        sum(denied_claim_flag) as denied_count
    from {{ ref('fct_claims') }}
    group by 1
),

collected as (
    select
        {{ dbt.date_trunc("month", "collection_date") }} as month,
        sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by 1
)

select
    cast(coalesce(b.month, c.month) as date) as month,
    coalesce(b.billed_amount, 0) as billed_amount,
    coalesce(c.collected_amount, 0) as collected_amount,
    round(100.0 * coalesce(c.collected_amount, 0) / nullif(b.billed_amount, 0), 2) as collection_rate_pct,
    coalesce(b.claim_count, 0) as claim_count,
    coalesce(b.denied_count, 0) as denied_count
from billed b
full outer join collected c on b.month = c.month
order by 1
