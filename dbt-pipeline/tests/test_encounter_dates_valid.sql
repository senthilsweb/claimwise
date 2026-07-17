-- Invariant: encounter_date in fct_encounters must be present and not in the future
select
    encounter_id,
    encounter_code,
    encounter_date
from {{ ref('fct_encounters') }}
where encounter_date is null
   or cast(encounter_date as date) > current_date
