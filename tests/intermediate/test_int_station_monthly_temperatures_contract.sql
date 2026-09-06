with parameters as (
    select *
    from {{ ref('int_analysis_parameters') }}
),

monthly as (
    select *
    from {{ ref('int_station_monthly_temperatures') }}
),

violations as (
    select
        monthly.station_id,
        monthly.month_start,
        'invalid monthly calculation' as violation
    from monthly
    cross join parameters
    where
        day(monthly.month_start) <> 1
        or monthly.expected_day_count <> day(last_day(monthly.month_start))
        or monthly.paired_day_count not between 0 and monthly.expected_day_count
        or monthly.monthly_completeness <> cast(
            monthly.paired_day_count * 1.0
                / monthly.expected_day_count
            as decimal(7, 6)
        )
        or (
            monthly.paired_day_count = 0
            and monthly.monthly_mean_temperature_c is not null
        )
        or (
            monthly.paired_day_count > 0
            and monthly.monthly_mean_temperature_c is null
        )
        or monthly.meets_monthly_completeness_threshold
            is distinct from (
                monthly.paired_day_count * 1.0
                    / monthly.expected_day_count
                    >= parameters.monthly_completeness_threshold
            )
),

duplicate_rows as (
    select
        station_id,
        month_start,
        'duplicate station-month grain' as violation
    from monthly
    group by station_id, month_start
    having count(*) > 1
)

select * from violations
union all
select * from duplicate_rows