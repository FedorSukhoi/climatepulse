with recent_months as (
    select *
    from {{ ref('int_station_monthly_temperatures') }}
    where analysis_period = 'recent'
),

baselines as (
    select *
    from {{ ref('int_station_monthly_baselines') }}
),

joined as (
    select
        recent.station_id,
        recent.month_start,
        recent.calendar_year,
        recent.calendar_month,
        recent.expected_day_count,
        recent.paired_day_count,
        recent.monthly_completeness,
        recent.monthly_mean_temperature_c,

        baselines.baseline_mean_temperature_c,
        baselines.eligible_baseline_years,
        baselines.expected_baseline_years,
        baselines.baseline_year_coverage,

        recent.meets_monthly_completeness_threshold
            as meets_recent_month_completeness_threshold,

        baselines.meets_baseline_coverage_threshold,

        recent.meets_monthly_completeness_threshold
            and baselines.meets_baseline_coverage_threshold
            as is_anomaly_eligible
    from recent_months as recent
    inner join baselines
        using (station_id, calendar_month)
),

final as (
    select
        *,
        case
            when is_anomaly_eligible
                then cast(
                    monthly_mean_temperature_c
                        - baseline_mean_temperature_c
                    as decimal(7, 3)
                )
        end as temperature_anomaly_c
    from joined
)

select *
from final