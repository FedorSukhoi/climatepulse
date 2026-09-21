with country_months as (

    select *

    from {{ ref('agg_country_monthly_anomalies') }}

),

target_geography as (

    select
        count(*) as eu27_target_country_count

    from {{ ref('stg_reference__countries') }}

),

aggregated as (

    select
        country_months.month_start,
        country_months.calendar_year,
        country_months.calendar_month,
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
            where country_months.has_eligible_station_contribution
        ) as included_country_count,
        count(*) as represented_country_universe_count,
        target_geography.eu27_target_country_count,
        count(*) filter (
            where country_months.has_eligible_station_contribution
        ) * 1.0 / count(*)
            as represented_country_coverage_ratio,
        count(*) filter (
            where country_months.has_eligible_station_contribution
        ) * 1.0
            / target_geography.eu27_target_country_count
            as eu27_target_country_coverage_ratio,
        avg(
            country_months.country_mean_temperature_anomaly_c
        ) filter (
            where country_months.has_eligible_station_contribution
        ) as equal_weight_included_country_mean_anomaly_c

    from country_months

    cross join target_geography

    group by
        country_months.month_start,
        country_months.calendar_year,
        country_months.calendar_month,
        target_geography.eu27_target_country_count

)

select *

from aggregated