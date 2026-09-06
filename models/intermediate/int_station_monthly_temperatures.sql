with daily_temperatures as (
    select *
    from {{ ref('int_station_daily_temperatures') }}
),

stations as (
    select station_id
    from {{ ref('stg_noaa__stations') }}
),

parameters as (
    select *
    from {{ ref('int_analysis_parameters') }}
),

month_series as (
    select generated_month::date as month_start
    from parameters
    cross join generate_series(
        date_trunc('month', baseline_start_date),
        date_trunc('month', recent_end_date),
        interval 1 month
    ) as generated(generated_month)
),

station_month_grid as (
    select
        stations.station_id,
        months.month_start
    from stations
    cross join month_series as months
),

observed_months as (
    select
        station_id,
        date_trunc('month', observation_date)::date as month_start,
        count(*) as paired_day_count,
        avg(daily_mean_temperature_c) as monthly_mean_temperature_c
    from daily_temperatures
    group by
        station_id,
        date_trunc('month', observation_date)::date
),

completed_months as (
    select
        grid.station_id,
        grid.month_start,
        year(grid.month_start) as calendar_year,
        month(grid.month_start) as calendar_month,
        day(last_day(grid.month_start)) as expected_day_count,
        coalesce(observed.paired_day_count, 0) as paired_day_count,
        observed.monthly_mean_temperature_c
    from station_month_grid as grid
    left join observed_months as observed
        using (station_id, month_start)
),

final as (
    select
        completed.station_id,
        completed.month_start,
        completed.calendar_year,
        completed.calendar_month,

        case
            when completed.month_start
                between date_trunc('month', parameters.baseline_start_date)
                and date_trunc('month', parameters.baseline_end_date)
                then 'baseline'
            when completed.month_start
                between date_trunc('month', parameters.recent_start_date)
                and date_trunc('month', parameters.recent_end_date)
                then 'recent'
        end as analysis_period,

        completed.expected_day_count,
        completed.paired_day_count,

        cast(
            completed.paired_day_count * 1.0
                / completed.expected_day_count
            as decimal(7, 6)
        ) as monthly_completeness,

        cast(
            completed.monthly_mean_temperature_c
            as decimal(7, 3)
        ) as monthly_mean_temperature_c,

        completed.paired_day_count * 1.0
            / completed.expected_day_count
            >= parameters.monthly_completeness_threshold
            as meets_monthly_completeness_threshold
    from completed_months as completed
    cross join parameters
)

select *
from final