with observations as (
    select *
    from {{ ref('stg_noaa__observations') }}
),

final_stations as (
    select station_id
    from {{ ref('stg_noaa__stations') }}
),

parameters as (
    select *
    from {{ ref('int_analysis_parameters') }}
),

eligible_observations as (
    select
        observations.station_id,
        observations.observation_date,
        observations.temperature_element,
        observations.temperature_c
    from observations
    inner join final_stations
        using (station_id)
    cross join parameters
    where observations.observation_date
        between parameters.baseline_start_date
        and parameters.recent_end_date
),

paired_temperatures as (
    select
        station_id,
        observation_date,

        max(
            case
                when temperature_element = 'TMAX'
                    then temperature_c
            end
        ) as maximum_temperature_c,

        max(
            case
                when temperature_element = 'TMIN'
                    then temperature_c
            end
        ) as minimum_temperature_c
    from eligible_observations
    group by
        station_id,
        observation_date
    having
        sum(
            case when temperature_element = 'TMAX' then 1 else 0 end
        ) = 1
        and sum(
            case when temperature_element = 'TMIN' then 1 else 0 end
        ) = 1
),

final as (
    select
        paired_temperatures.station_id,
        paired_temperatures.observation_date,
        year(paired_temperatures.observation_date) as calendar_year,
        month(paired_temperatures.observation_date) as calendar_month,
        paired_temperatures.maximum_temperature_c,
        paired_temperatures.minimum_temperature_c,

        cast(
            (
                paired_temperatures.maximum_temperature_c
                + paired_temperatures.minimum_temperature_c
            ) / 2.0
            as decimal(6, 2)
        ) as daily_mean_temperature_c,

        case
            when paired_temperatures.observation_date
                between parameters.baseline_start_date
                and parameters.baseline_end_date
                then 'baseline'
            when paired_temperatures.observation_date
                between parameters.recent_start_date
                and parameters.recent_end_date
                then 'recent'
        end as analysis_period
    from paired_temperatures
    cross join parameters
)

select *
from final