with final_stations as (

    select *

    from {{ ref('stg_noaa__stations') }}

),

final as (

    select
        station_id,
        noaa_country_code,
        iso_alpha2,
        country_name,
        station_name,
        latitude,
        longitude,
        elevation_m,
        baseline_completeness,
        recent_completeness,
        baseline_min_monthly_completeness,
        recent_min_monthly_completeness

    from final_stations

)

select *

from final