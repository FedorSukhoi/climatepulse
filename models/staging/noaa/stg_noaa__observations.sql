with source_data as (
    select *
    from {{ source('noaa', 'daily_observations') }}
),

filtered_and_renamed as (
    select
        station_id,
        observation_date,
        element as temperature_element,
        cast(data_value / 10.0 as decimal(6, 1)) as temperature_c,
        measurement_flag,
        source_flag,
        observation_time,
        source_file,
        ingested_at_utc
    from source_data
    where
        quality_flag is null
        and data_value <> -9999
)

select *
from filtered_and_renamed