-- Checks if the table contains exactly 27 unique NOAA and ISO codes.

with country_summary as (
    select
        count(*) as country_count,
        count(distinct noaa_country_code) as noaa_code_count,
        count(distinct iso_alpha2) as iso_code_count
    from {{ source('climatepulse_inputs', 'countries') }}
)

select *
from country_summary
where
    country_count <> 27
    or noaa_code_count <> 27
    or iso_code_count <> 27