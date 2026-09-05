-- Verifies station's consistent mapping

select
    stations.station_id,
    stations.noaa_country_code,
    stations.iso_alpha2,
    stations.country_name
from {{ ref('stg_noaa__stations') }} as stations
left join {{ ref('stg_reference__countries') }} as countries
    on stations.noaa_country_code = countries.noaa_country_code
    and stations.iso_alpha2 = countries.iso_alpha2
    and stations.country_name = countries.country_name
where countries.noaa_country_code is null