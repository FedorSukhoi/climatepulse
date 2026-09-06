{{ config(materialized='view') }}

with parameters as (
    select *
    from {{ ref('stg_reference__analysis_parameters') }}
),

typed_parameters as (
    select
        cast(
            max(
                case
                    when parameter_name = 'baseline_start_date'
                        then parameter_value
                end
            ) as date
        ) as baseline_start_date,

        cast(
            max(
                case
                    when parameter_name = 'baseline_end_date'
                        then parameter_value
                end
            ) as date
        ) as baseline_end_date,

        cast(
            max(
                case
                    when parameter_name = 'recent_start_date'
                        then parameter_value
                end
            ) as date
        ) as recent_start_date,

        cast(
            max(
                case
                    when parameter_name = 'recent_end_date'
                        then parameter_value
                end
            ) as date
        ) as recent_end_date,

        cast(
            max(
                case
                    when parameter_name = 'overall_completeness_threshold'
                        then parameter_value
                end
            ) as decimal(4, 2)
        ) as overall_completeness_threshold,

        cast(
            max(
                case
                    when parameter_name = 'monthly_completeness_threshold'
                        then parameter_value
                end
            ) as decimal(4, 2)
        ) as monthly_completeness_threshold
    from parameters
)

select *
from typed_parameters