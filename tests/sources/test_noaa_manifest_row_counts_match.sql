with observation_counts as (
    select
        source_file,
        count(*) as observed_temperature_rows
    from {{ source('noaa', 'daily_observations') }}
    group by source_file
),

manifest_counts as (
    select
        source_file,
        temperature_row_count as documented_temperature_rows
    from {{ source('noaa', 'file_manifest') }}
)

select
    coalesce(
        observations.source_file,
        manifest.source_file
    ) as source_file,
    observations.observed_temperature_rows,
    manifest.documented_temperature_rows
from observation_counts as observations
full outer join manifest_counts as manifest
    using (source_file)
where
    observations.observed_temperature_rows
        is distinct from manifest.documented_temperature_rows