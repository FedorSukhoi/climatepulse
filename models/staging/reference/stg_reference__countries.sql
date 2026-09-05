with source_data as (
    select *
    from {{ source('climatepulse_inputs', 'countries') }}
),

renamed as (
    select
        noaa_country_code,
        iso_alpha2,
        country_name,
        source_file,
        ingested_at_utc
    from source_data
)

select *
from renamed