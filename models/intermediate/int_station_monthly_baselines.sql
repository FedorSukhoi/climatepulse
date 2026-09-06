with monthly_temperatures as (
    select *
    from {{ ref('int_station_monthly_temperatures') }}
    where analysis_period = 'baseline'
),

parameters as (
    select *
    from {{ ref('int_analysis_parameters') }}
),

baseline_statistics as (
    select
        station_id,
        calendar_month,

        count_if(
            meets_monthly_completeness_threshold
        ) as eligible_baseline_years,

        avg(monthly_mean_temperature_c) filter (
            where meets_monthly_completeness_threshold
        ) as baseline_mean_temperature_c
    from monthly_temperatures
    group by
        station_id,
        calendar_month
),

final as (
    select
        statistics.station_id,
        statistics.calendar_month,

        cast(
            statistics.baseline_mean_temperature_c
            as decimal(7, 3)
        ) as baseline_mean_temperature_c,

        statistics.eligible_baseline_years,

        date_diff(
            'year',
            parameters.baseline_start_date,
            parameters.baseline_end_date
        ) + 1 as expected_baseline_years,

        cast(
            statistics.eligible_baseline_years * 1.0
                / (
                    date_diff(
                        'year',
                        parameters.baseline_start_date,
                        parameters.baseline_end_date
                    ) + 1
                )
            as decimal(7, 6)
        ) as baseline_year_coverage,

        cast(
            ceil(
                (
                    date_diff(
                        'year',
                        parameters.baseline_start_date,
                        parameters.baseline_end_date
                    ) + 1
                ) * parameters.monthly_completeness_threshold
            )
            as integer
        ) as minimum_required_baseline_years,

        statistics.eligible_baseline_years >= ceil(
            (
                date_diff(
                    'year',
                    parameters.baseline_start_date,
                    parameters.baseline_end_date
                ) + 1
            ) * parameters.monthly_completeness_threshold
        ) as meets_baseline_coverage_threshold
    from baseline_statistics as statistics
    cross join parameters
)

select *
from final