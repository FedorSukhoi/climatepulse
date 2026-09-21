with country_months as (

    select *

    from {{ ref('agg_country_monthly_anomalies') }}

),

invalid_rows as (

    select
        iso_alpha2,
        month_start,
        'invalid country-month attributes' as violation

    from country_months

    where
        month_start not between date '2021-01-01' and date '2025-12-01'
        or month_start
            <> cast(date_trunc('month', month_start) as date)
        or calendar_year <> extract(year from month_start)
        or calendar_month <> extract(month from month_start)
        or calendar_month not between 1 and 12
        or total_final_stations <= 0
        or eligible_contributing_stations < 0
        or eligible_contributing_stations > total_final_stations
        or station_contribution_ratio not between 0 and 1
        or abs(
            station_contribution_ratio
                - eligible_contributing_stations * 1.0
                    / total_final_stations
        ) > 0.000000000001
        or has_eligible_station_contribution is distinct from (
            eligible_contributing_stations > 0
        )
        or (
            has_eligible_station_contribution
            and country_mean_temperature_anomaly_c is null
        )
        or (
            not has_eligible_station_contribution
            and country_mean_temperature_anomaly_c is not null
        )

),

duplicate_rows as (

    select
        iso_alpha2,
        month_start,
        'duplicate country-month' as violation

    from country_months

    group by iso_alpha2, month_start

    having count(*) > 1

),

dimension_station_counts as (

    select
        iso_alpha2,
        count(*) as expected_station_count

    from {{ ref('dim_locations') }}

    group by iso_alpha2

),

invalid_station_counts as (

    select
        country_months.iso_alpha2,
        country_months.month_start,
        'country station count does not reconcile' as violation

    from country_months

    inner join dimension_station_counts
        using (iso_alpha2)

    where
        country_months.total_final_stations
            <> dimension_station_counts.expected_station_count

),

summary_metrics as (

    select
        count(*) as row_count,
        count(distinct iso_alpha2) as country_count,
        count(distinct month_start) as month_count

    from country_months

),

invalid_summary as (

    select
        cast(null as varchar) as iso_alpha2,
        cast(null as date) as month_start,
        'unexpected country-month grid dimensions' as violation

    from summary_metrics

    where
        row_count <> 900
        or country_count <> 15
        or month_count <> 60

)

select * from invalid_rows

union all

select * from duplicate_rows

union all

select * from invalid_station_counts

union all

select * from invalid_summary