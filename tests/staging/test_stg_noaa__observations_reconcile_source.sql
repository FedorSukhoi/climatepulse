-- Verifies that filtered row count or temperature count/sum/range does not differ from the raw-source calculation. This also verifies the Celsius conversion collectively.

with expected as (
    select
        count(*) as row_count,
        sum(data_value) as temperature_tenths_sum,
        min(data_value) as minimum_value,
        max(data_value) as maximum_value
    from {{ source('noaa', 'daily_observations') }}
    where
        quality_flag is null
        and data_value <> -9999
),

actual as (
    select
        count(*) as row_count,
        sum(temperature_c * 10) as temperature_tenths_sum,
        min(temperature_c * 10) as minimum_value,
        max(temperature_c * 10) as maximum_value
    from {{ ref('stg_noaa__observations') }}
)

select
    expected.row_count as expected_row_count,
    actual.row_count as actual_row_count,
    expected.temperature_tenths_sum as expected_sum,
    actual.temperature_tenths_sum as actual_sum,
    expected.minimum_value as expected_minimum,
    actual.minimum_value as actual_minimum,
    expected.maximum_value as expected_maximum,
    actual.maximum_value as actual_maximum
from expected
cross join actual
where
    expected.row_count is distinct from actual.row_count
    or expected.temperature_tenths_sum
        is distinct from actual.temperature_tenths_sum
    or expected.minimum_value is distinct from actual.minimum_value
    or expected.maximum_value is distinct from actual.maximum_value