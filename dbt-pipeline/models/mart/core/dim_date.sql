with date_spine as (
    {{ dbt_date.get_date_dimension(
        start_date="2023-01-01",
        end_date="2024-12-31"
    ) }}
)
select
    date_day as date_id,
    date_day as full_date,
    {{ dbt_date.date_part('year', 'date_day') }} as year, -- Correct macro for extracting the year
    {{ dbt_date.date_part('month', 'date_day') }} as month_number,
    {{ dbt_date.month_name('date_day') }} as month_name, -- Extracts month name
    {{ dbt_date.date_part('quarter', 'date_day') }} as quarter,
    {{ dbt_date.day_of_week('date_day') }} as day_of_week,
    {{ dbt_date.day_name('date_day') }} as day_name, -- Extracts day name
    {{ dbt_date.iso_week_end('date_day') }} as is_weekend,
    {{ dbt_date.iso_week_start('date_day') }} as week_start_date,
    {{ dbt_date.week_end('date_day') }} as week_end_date
from date_spine
