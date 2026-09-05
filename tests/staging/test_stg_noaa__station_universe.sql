-- Verifies that the staged universe is exactly 640 stations and 15 countries.

with station_summary as (
    select
        count(*) as station_count,
        count(distinct iso_alpha2) as represented_country_count
    from {{ ref('stg_noaa__stations') }}
)

select *
from station_summary
where
    station_count <> 640
    or represented_country_count <> 15