-- Verifies that no more than one row exists for a station, date, and temperature element.

select
    station_id,
    observation_date,
    temperature_element,
    count(*) as record_count
from {{ ref('stg_noaa__observations') }}
group by
    station_id,
    observation_date,
    temperature_element
having count(*) > 1