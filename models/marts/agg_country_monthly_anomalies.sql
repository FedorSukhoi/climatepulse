with anomalies as (

    select *

    from {{ ref('fct_anomalies') }}

),

locations as (

    select *

    from {{ ref('dim_locations') }}

),

station_months as (

    select
        anomalies.month_start,
        anomalies.calendar_year,
        anomalies.calendar_month,
        locations.noaa_country_code,
        locations.iso_alpha2,
        locations.country_name,
        anomalies.station_id,
        anomalies.is_anomaly_eligible,
        anomalies.temperature_anomaly_c

    from anomalies

    inner join locations
        using (station_id)

),

country_months as (

    select
        month_start,
        calendar_year,
        calendar_month,
        noaa_country_code,
        iso_alpha2,
        country_name,
        count(*) as total_final_stations,
        count(*) filter (
            where is_anomaly_eligible
        ) as eligible_contributing_stations,
        count(*) filter (
            where is_anomaly_eligible
        ) * 1.0 / count(*) as station_contribution_ratio,
        avg(temperature_anomaly_c) filter (
            where is_anomaly_eligible
        ) as country_mean_temperature_anomaly_c

    from station_months

    group by
        month_start,
        calendar_year,
        calendar_month,
        noaa_country_code,
        iso_alpha2,
        country_name

),

final as (

    select
        month_start,
        calendar_year,
        calendar_month,
        noaa_country_code,
        iso_alpha2,
        country_name,
        total_final_stations,
        eligible_contributing_stations,
        station_contribution_ratio,
        eligible_contributing_stations > 0
            as has_eligible_station_contribution,
        country_mean_temperature_anomaly_c

    from country_months

)

select *

from final