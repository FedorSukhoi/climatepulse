-- Verifies that no station has out-of-range latitude, longitude, or completeness values.

select
    station_id
from {{ ref('stg_noaa__stations') }}
where
    latitude not between -90 and 90
    or longitude not between -180 and 180
    or baseline_completeness not between 0.80 and 1.00
    or recent_completeness not between 0.80 and 1.00
    or baseline_min_monthly_completeness not between 0.70 and 1.00
    or recent_min_monthly_completeness not between 0.70 and 1.00