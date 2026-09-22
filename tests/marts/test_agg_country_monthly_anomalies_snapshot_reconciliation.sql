{{ config(tags=['production_snapshot']) }}

with coverage_summary as (

    select
        count(*) as country_month_rows,
        count(*) filter (
            where eligible_contributing_stations = 0
        ) as zero_contributor_country_months,
        count(*) filter (
            where eligible_contributing_stations
                < total_final_stations
        ) as incomplete_country_months

    from {{ ref('agg_country_monthly_anomalies') }}

)

select *

from coverage_summary

where
    country_month_rows <> 900
    or zero_contributor_country_months <> 35
    or incomplete_country_months <> 153