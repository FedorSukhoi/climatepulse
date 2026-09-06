with parameters as (
    select *
    from {{ ref('int_analysis_parameters') }}
),

invalid_rows as (
    select
        daily.station_id,
        daily.observation_date,
        'invalid daily value or classification' as violation
    from {{ ref('int_station_daily_temperatures') }} as daily
    cross join parameters
    where
        daily.maximum_temperature_c < daily.minimum_temperature_c
        or daily.daily_mean_temperature_c <> cast(
            (
                daily.maximum_temperature_c
                + daily.minimum_temperature_c
            ) / 2.0
            as decimal(6, 2)
        )
        or daily.observation_date not between
            parameters.baseline_start_date
            and parameters.recent_end_date
        or daily.analysis_period is distinct from
            case
                when daily.observation_date between
                    parameters.baseline_start_date
                    and parameters.baseline_end_date
                    then 'baseline'
                else 'recent'
            end
),

duplicate_rows as (
    select
        station_id,
        observation_date,
        'duplicate station-day grain' as violation
    from {{ ref('int_station_daily_temperatures') }}
    group by station_id, observation_date
    having count(*) > 1
)

select * from invalid_rows
union all
select * from duplicate_rows