with baselines as (
    select *
    from {{ ref('int_station_monthly_baselines') }}
),

invalid_rows as (
    select
        station_id,
        calendar_month,
        'invalid baseline coverage calculation' as violation
    from baselines
    where
        calendar_month not between 1 and 12
        or eligible_baseline_years not between 0 and 30
        or expected_baseline_years <> 30
        or minimum_required_baseline_years <> 21
        or baseline_year_coverage <> cast(
            eligible_baseline_years * 1.0
                / expected_baseline_years
            as decimal(7, 6)
        )
        or meets_baseline_coverage_threshold
            is distinct from (
                eligible_baseline_years
                >= minimum_required_baseline_years
            )
),

duplicate_rows as (
    select
        station_id,
        calendar_month,
        'duplicate station/calendar-month baseline' as violation
    from baselines
    group by station_id, calendar_month
    having count(*) > 1
)

select * from invalid_rows
union all
select * from duplicate_rows