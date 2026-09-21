with expected as (

    select
        locations.iso_alpha2,
        anomalies.month_start,
        count(*) as total_final_stations,
        count(*) filter (
            where anomalies.is_anomaly_eligible
        ) as eligible_contributing_stations,
        count(*) filter (
            where anomalies.is_anomaly_eligible
        ) * 1.0 / count(*) as station_contribution_ratio,
        avg(anomalies.temperature_anomaly_c) filter (
            where anomalies.is_anomaly_eligible
        ) as country_mean_temperature_anomaly_c

    from {{ ref('fct_anomalies') }} as anomalies

    inner join {{ ref('dim_locations') }} as locations
        using (station_id)

    group by
        locations.iso_alpha2,
        anomalies.month_start

),

actual as (

    select *

    from {{ ref('agg_country_monthly_anomalies') }}

)

select
    coalesce(actual.iso_alpha2, expected.iso_alpha2) as iso_alpha2,
    coalesce(actual.month_start, expected.month_start) as month_start,
    'country aggregation does not reconcile' as violation

from actual

full outer join expected
    on actual.iso_alpha2 = expected.iso_alpha2
    and actual.month_start = expected.month_start

where
    actual.iso_alpha2 is null
    or expected.iso_alpha2 is null
    or actual.total_final_stations
        <> expected.total_final_stations
    or actual.eligible_contributing_stations
        <> expected.eligible_contributing_stations
    or abs(
        actual.station_contribution_ratio
            - expected.station_contribution_ratio
    ) > 0.000000000001
    or (
        actual.country_mean_temperature_anomaly_c is null
    ) is distinct from (
        expected.country_mean_temperature_anomaly_c is null
    )
    or (
        actual.country_mean_temperature_anomaly_c is not null
        and abs(
            actual.country_mean_temperature_anomaly_c
                - expected.country_mean_temperature_anomaly_c
        ) > 0.000000000001
    )