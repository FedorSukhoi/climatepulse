with monthly_aggregates as (

    select *

    from {{ ref('agg_included_countries_monthly_anomalies') }}

),

invalid_rows as (

    select
        month_start,
        'invalid included-country monthly aggregate' as violation

    from monthly_aggregates

    where
        month_start not between date '2021-01-01' and date '2025-12-01'
        or month_start
            <> cast(date_trunc('month', month_start) as date)
        or calendar_year <> extract(year from month_start)
        or calendar_month <> extract(month from month_start)
        or calendar_month not between 1 and 12
        or eligible_contributing_station_count < 0
        or represented_station_universe_count <> (select count(*) from {{ ref('dim_locations') }})
        or eligible_contributing_station_count
            > represented_station_universe_count
        or station_contribution_ratio not between 0 and 1
        or abs(
            station_contribution_ratio
                - eligible_contributing_station_count * 1.0
                    / represented_station_universe_count
        ) > 0.000000000001
        or included_country_count < 0
        or included_country_count
            > represented_country_universe_count
        or represented_country_universe_count <> (select count(distinct iso_alpha2) from {{ ref('dim_locations') }})
        or eu27_target_country_count <> 27
        or represented_country_coverage_ratio not between 0 and 1
        or eu27_target_country_coverage_ratio not between 0 and 1
        or abs(
            represented_country_coverage_ratio
                - included_country_count * 1.0
                    / represented_country_universe_count
        ) > 0.000000000001
        or abs(
            eu27_target_country_coverage_ratio
                - included_country_count * 1.0
                    / eu27_target_country_count
        ) > 0.000000000001
        or (
            included_country_count = 0
            and equal_weight_included_country_mean_anomaly_c is not null
        )
        or (
            included_country_count > 0
            and equal_weight_included_country_mean_anomaly_c is null
        )

),

summary_metrics as (

    select
        count(*) as row_count,
        count(distinct month_start) as month_count

    from monthly_aggregates

),

invalid_summary as (

    select
        cast(null as date) as month_start,
        'unexpected monthly aggregate grid dimensions' as violation

    from summary_metrics

    where
        row_count <> 60
        or month_count <> 60

)

select * from invalid_rows

union all

select * from invalid_summary