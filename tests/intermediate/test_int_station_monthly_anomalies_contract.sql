with anomalies as (
    select *
    from {{ ref('int_station_monthly_anomalies') }}
),

invalid_rows as (
    select
        station_id,
        month_start,
        'invalid anomaly calculation or eligibility' as violation
    from anomalies
    where
        month_start not between date '2021-01-01' and date '2025-12-01'
        or is_anomaly_eligible is distinct from (
            meets_recent_month_completeness_threshold
            and meets_baseline_coverage_threshold
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
        'duplicate station-month anomaly' as violation
    from anomalies
    group by station_id, month_start
    having count(*) > 1
)

select * from invalid_rows
union all
select * from duplicate_rows