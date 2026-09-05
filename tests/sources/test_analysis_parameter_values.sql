-- Checks if any of the six frozen parameter values is missing, changed, or unexpected.

with expected_parameters(parameter, value) as (
    values
        ('baseline_start_date', '1991-01-01'),
        ('baseline_end_date', '2020-12-31'),
        ('recent_start_date', '2021-01-01'),
        ('recent_end_date', '2025-12-31'),
        ('overall_completeness_threshold', '0.80'),
        ('monthly_completeness_threshold', '0.70')
),

actual_parameters as (
    select
        parameter,
        value
    from {{ source('climatepulse_inputs', 'analysis_parameters') }}
)

select
    coalesce(expected.parameter, actual.parameter) as parameter,
    expected.value as expected_value,
    actual.value as actual_value
from expected_parameters as expected
full outer join actual_parameters as actual
    using (parameter)
where expected.value is distinct from actual.value