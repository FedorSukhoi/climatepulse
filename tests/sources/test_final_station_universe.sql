-- Verifies that the frozen universe contains exactly 640 stations across 15 countries.

with station_summary as (
    select
        count(*) as station_count,
        count(distinct iso_alpha2) as represented_country_count
    from {{ source('climatepulse_inputs', 'final_stations') }}
)

select *
from station_summary
where
    station_count <> 640
    or represented_country_count <> 15