with station_monthly_anomalies as (

    select *

    from {{ ref('int_station_monthly_anomalies') }}

),

final as (

    select
        station_id,
        month_start,
        calendar_year,
        calendar_month,
        expected_day_count,
        paired_day_count,
        monthly_completeness,
        monthly_mean_temperature_c,
        baseline_mean_temperature_c,
        eligible_baseline_years,
        expected_baseline_years,
        baseline_year_coverage,
        meets_recent_month_completeness_threshold,
        meets_baseline_coverage_threshold,
        is_anomaly_eligible,
        temperature_anomaly_c

    from station_monthly_anomalies

)

select *

from final