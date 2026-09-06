with grid_summary as (
    select
        count(*) as row_count,
        count(distinct station_id) as station_count,
        min(month_start) as minimum_month,
        max(month_start) as maximum_month
    from {{ ref('int_station_monthly_temperatures') }}
)

select *
from grid_summary
where
    row_count <> 268800
    or station_count <> 640
    or minimum_month <> date '1991-01-01'
    or maximum_month <> date '2025-12-01'