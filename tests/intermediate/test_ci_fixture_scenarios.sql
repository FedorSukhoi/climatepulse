{{ config(enabled=(target.name == 'ci')) }}

with checks as (
    select 'baseline 20 years rejected' as scenario
    where not exists (
        select 1 from {{ ref('int_station_monthly_baselines') }}
        where station_id = 'GM000000002' and calendar_month = 1
          and eligible_baseline_years = 20 and not meets_baseline_coverage_threshold
    )
    union all
    select 'baseline 21 years accepted'
    where not exists (
        select 1 from {{ ref('int_station_monthly_baselines') }}
        where station_id = 'AU000000001' and calendar_month = 1
          and eligible_baseline_years = 21 and meets_baseline_coverage_threshold
    )
    union all
    select 'January 70 percent boundary'
    where not exists (
        select 1 from {{ ref('int_station_monthly_temperatures') }}
        where station_id = 'GM000000001' and month_start = date '2022-01-01'
          and paired_day_count = 21 and not meets_monthly_completeness_threshold
    ) or not exists (
        select 1 from {{ ref('int_station_monthly_temperatures') }}
        where station_id = 'GM000000002' and month_start = date '2022-01-01'
          and paired_day_count = 22 and meets_monthly_completeness_threshold
    )
    union all
    select 'empty station month retained'
    where not exists (
        select 1 from {{ ref('int_station_monthly_temperatures') }}
        where station_id = 'AU000000001' and month_start = date '2021-01-01'
          and paired_day_count = 0 and monthly_mean_temperature_c is null
    )
    union all
    select 'flag sentinel and missing pair rejected'
    where (select count(*) from {{ ref('int_station_daily_temperatures') }}
           where station_id = 'GM000000002' and observation_date between date '2021-03-01' and date '2021-03-04') <> 0
    union all
    select '2026 excluded'
    where exists (select 1 from {{ ref('fct_anomalies') }} where month_start >= date '2026-01-01')
    union all
    select 'ineligible anomaly remains null'
    where not exists (
        select 1 from {{ ref('fct_anomalies') }}
        where station_id = 'GM000000002' and month_start = date '2021-01-01'
          and not is_anomaly_eligible and temperature_anomaly_c is null
    )
    union all
    select 'zero contributor country month'
    where not exists (
        select 1 from {{ ref('agg_country_monthly_anomalies') }}
        where iso_alpha2 = 'AT' and month_start = date '2021-01-01'
          and eligible_contributing_stations = 0 and country_mean_temperature_anomaly_c is null
    )
    union all
    select 'country-first differs from station mean'
    where not exists (
        select 1 from {{ ref('agg_included_countries_monthly_anomalies') }}
        where month_start = date '2021-02-01'
          and included_country_count = 2 and eligible_contributing_station_count = 3
          and abs(equal_weight_included_country_mean_anomaly_c - 5.0) < 0.001
    )
)
select * from checks
