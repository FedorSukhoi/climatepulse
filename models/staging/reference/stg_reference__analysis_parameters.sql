with source_data as (
    select *
    from {{ source('climatepulse_inputs', 'analysis_parameters') }}
),

renamed as (
    select
        parameter as parameter_name,
        value as parameter_value,
        description,
        source_file,
        ingested_at_utc
    from source_data
)

select *
from renamed