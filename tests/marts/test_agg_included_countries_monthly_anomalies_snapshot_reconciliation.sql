{{ config(tags=['production_snapshot']) }}

with coverage_summary as (

    select
        count(*) as monthly_rows,
        min(included_country_count) as minimum_included_countries,
        max(included_country_count) as maximum_included_countries,
        count(*) filter (
            where included_country_count < 15
        ) as months_below_fifteen_countries

    from {{ ref('agg_included_countries_monthly_anomalies') }}

)

select *

from coverage_summary

where
    monthly_rows <> 60
    or minimum_included_countries <> 13
    or maximum_included_countries <> 15
    or months_below_fifteen_countries <> 23