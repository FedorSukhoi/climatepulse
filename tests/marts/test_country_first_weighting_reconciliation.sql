with station_months as (

    select
        anomalies.month_start,
        locations.iso_alpha2,
        anomalies.is_anomaly_eligible,
        anomalies.temperature_anomaly_c

    from {{ ref('fct_anomalies') }} as anomalies

    inner join {{ ref('dim_locations') }} as locations
        using (station_id)

),

country_months as (

    select
        month_start,
        iso_alpha2,
        count(*) as total_final_stations,
        count(*) filter (
            where is_anomaly_eligible
        ) as eligible_contributing_stations,
        avg(temperature_anomaly_c) filter (
            where is_anomaly_eligible
        ) as country_mean_temperature_anomaly_c

    from station_months

    group by month_start, iso_alpha2

),

target_geography as (

    select
        count(*) as eu27_target_country_count

    from {{ ref('stg_reference__countries') }}

),

expected as (

    select
        country_months.month_start,
        sum(
            country_months.eligible_contributing_stations
        ) as eligible_contributing_station_count,
        sum(
            country_months.total_final_stations
        ) as represented_station_universe_count,
        sum(
            country_months.eligible_contributing_stations
        ) * 1.0
            / sum(country_months.total_final_stations)
            as station_contribution_ratio,
        count(*) filter (
            where country_mean_temperature_anomaly_c is not null
        ) as included_country_count,
        count(*) as represented_country_universe_count,
        target_geography.eu27_target_country_count,
        count(*) filter (
            where country_mean_temperature_anomaly_c is not null
        ) * 1.0 / count(*)
            as represented_country_coverage_ratio,
        count(*) filter (
            where country_mean_temperature_anomaly_c is not null
        ) * 1.0
            / target_geography.eu27_target_country_count
            as eu27_target_country_coverage_ratio,
        avg(country_mean_temperature_anomaly_c) filter (
            where country_mean_temperature_anomaly_c is not null
        ) as equal_weight_included_country_mean_anomaly_c

    from country_months

    cross join target_geography

    group by
        country_months.month_start,
        target_geography.eu27_target_country_count

),

actual as (

    select *

    from {{ ref('agg_included_countries_monthly_anomalies') }}

)

select
    coalesce(actual.month_start, expected.month_start) as month_start,
    'country-first aggregation does not reconcile' as violation

from actual

full outer join expected
    on actual.month_start = expected.month_start

where
    actual.month_start is null
    or expected.month_start is null
    or actual.eligible_contributing_station_count
        <> expected.eligible_contributing_station_count
    or actual.represented_station_universe_count
        <> expected.represented_station_universe_count
    or abs(
        actual.station_contribution_ratio
            - expected.station_contribution_ratio
    ) > 0.000000000001
    or actual.included_country_count
        <> expected.included_country_count
    or actual.represented_country_universe_count
        <> expected.represented_country_universe_count
    or actual.eu27_target_country_count
        <> expected.eu27_target_country_count
    or abs(
        actual.represented_country_coverage_ratio
            - expected.represented_country_coverage_ratio
    ) > 0.000000000001
    or abs(
        actual.eu27_target_country_coverage_ratio
            - expected.eu27_target_country_coverage_ratio
    ) > 0.000000000001
    or (
        actual.equal_weight_included_country_mean_anomaly_c is null
    ) is distinct from (
        expected.equal_weight_included_country_mean_anomaly_c is null
    )
    or (
        actual.equal_weight_included_country_mean_anomaly_c is not null
        and abs(
            actual.equal_weight_included_country_mean_anomaly_c
                - expected.equal_weight_included_country_mean_anomaly_c
        ) > 0.000000000001
    )