with anomalies as (

    select *

    from {{ ref('fct_anomalies') }}

),

invalid_rows as (

    select
        station_id,
        month_start,
        'invalid anomaly fact attributes' as violation

    from anomalies

    where
        month_start not between date '2021-01-01' and date '2025-12-01'
        or month_start
            <> cast(date_trunc('month', month_start) as date)
        or calendar_year <> extract(year from month_start)
        or calendar_month <> extract(month from month_start)
        or calendar_month not between 1 and 12
        or expected_day_count not between 28 and 31
        or paired_day_count < 0
        or paired_day_count > expected_day_count
        or monthly_completeness not between 0 and 1
        or eligible_baseline_years < 0
        or eligible_baseline_years > expected_baseline_years
        or baseline_year_coverage not between 0 and 1
        or is_anomaly_eligible is distinct from (
            meets_recent_month_completeness_threshold
            and meets_baseline_coverage_threshold
        )
        or (
            is_anomaly_eligible
            and monthly_mean_temperature_c is null
        )
        or (
            is_anomaly_eligible
            and temperature_anomaly_c is null
        )
        or (
            not is_anomaly_eligible
            and temperature_anomaly_c is not null
        )
        or (
            is_anomaly_eligible
            and temperature_anomaly_c <> cast(
                monthly_mean_temperature_c
                    - baseline_mean_temperature_c
                as decimal(7, 3)
            )
        )

),

duplicate_rows as (

    select
        station_id,
        month_start,
        'duplicate station-month fact' as violation

    from anomalies

    group by station_id, month_start

    having count(*) > 1

),

summary_metrics as (

    select
        count(*) as row_count,
        count(distinct station_id) as station_count,
        count(distinct month_start) as month_count

    from anomalies

),

invalid_summary as (

    select
        cast(null as varchar) as station_id,
        cast(null as date) as month_start,
        'unexpected fact grid dimensions' as violation

    from summary_metrics

    where
        row_count <> 38400
        or station_count <> 640
        or month_count <> 60

)

select * from invalid_rows

union all

select * from duplicate_rows

union all

select * from invalid_summary