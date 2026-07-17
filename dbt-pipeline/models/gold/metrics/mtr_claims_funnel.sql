-- Metric layer: claim lifecycle funnel by status.
{{ config(materialized='table') }}

select
    claim_status,
    count(*) as claim_count,
    round(sum(claim_amount), 2) as total_amount,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as pct_of_claims
from {{ ref('fct_claims') }}
group by claim_status
order by claim_count desc
