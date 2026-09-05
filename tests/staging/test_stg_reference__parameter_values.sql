-- Verifies that the staged reference parameters are consistent with the expected values.

with expected_parameters(parameter_name, parameter_value) as (
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
        parameter_name,
        parameter_value
    from {{ ref('stg_reference__analysis_parameters') }}
)

select
    coalesce(
        expected.parameter_name,
        actual.parameter_name
    ) as parameter_name,
    expected.parameter_value as expected_value,
    actual.parameter_value as actual_value
from expected_parameters as expected
full outer join actual_parameters as actual
    using (parameter_name)
where
    expected.parameter_value
        is distinct from actual.parameter_value