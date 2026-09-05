with source_data as (
    select *
    from {{ source('climatepulse_inputs', 'final_stations') }}
),

renamed as (
    select
        station_id,
        noaa_country_code,
        iso_alpha2,
        country_name,
        station_name,
        latitude,
        longitude,
        elevation_m,
        baseline_completeness,
        recent_completeness,
        baseline_min_monthly_completeness,
        recent_min_monthly_completeness,
        source_file,
        ingested_at_utc
    from source_data
)

select *
from renamed