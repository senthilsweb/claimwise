-- Metric layer: single-row executive KPI summary. Every headline number on
-- the dashboard comes from here — defined once, consumed everywhere.
{{ config(materialized='table') }}

with collected_per_claim as (
    select claim_key, sum(collected_amount) as collected_amount
    from {{ ref('fct_collections') }}
    group by claim_key
),

claims as (
    select
        sum(f.claim_amount) as gross_billed,
        sum(coalesce(c.collected_amount, 0)) as total_collected,
        count(*) as claim_count,
        sum(f.denied_claim_flag) as denied_count,
        sum(case
            when f.claim_status != 'Denied'
             and f.claim_amount - coalesce(c.collected_amount, 0) > 0
            then f.claim_amount - coalesce(c.collected_amount, 0)
            else 0
        end) as open_ar
    from {{ ref('fct_claims') }} f
    left join collected_per_claim c on f.claim_id = c.claim_key
),

cycle as (
    select round(avg({{ dbt.datediff("dateCreated", "dateUpdated", "day") }}), 1) as avg_cycle_days
    from {{ ref('stg_claims') }}
),

encounters as (
    select count(*) as encounter_count
    from {{ ref('fct_encounters') }}
)

select
    round(cl.gross_billed, 2) as gross_billed,
    round(cl.total_collected, 2) as total_collected,
    round(100.0 * cl.total_collected / nullif(cl.gross_billed, 0), 2) as collection_rate_pct,
    round(100.0 * cl.denied_count / nullif(cl.claim_count, 0), 2) as denial_rate_pct,
    round(cl.open_ar, 2) as open_ar,
    cy.avg_cycle_days,
    cl.claim_count,
    e.encounter_count
from claims cl
cross join cycle cy
cross join encounters e
