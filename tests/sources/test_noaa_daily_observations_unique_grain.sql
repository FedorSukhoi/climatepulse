select
    station_id,
    observation_date,
    element,
    count(*) as record_count
from {{ source('noaa', 'daily_observations') }}
group by
    station_id,
    observation_date,
    element
having count(*) > 1