-- Checks if any station violates the 80% overall or 70% monthly completeness rule.

select
    station_id,
    baseline_completeness,
    recent_completeness,
    baseline_min_monthly_completeness,
    recent_min_monthly_completeness
from {{ source('climatepulse_inputs', 'final_stations') }}
where
    baseline_completeness not between 0.80 and 1.00
    or recent_completeness not between 0.80 and 1.00
    or baseline_min_monthly_completeness not between 0.70 and 1.00
    or recent_min_monthly_completeness not between 0.70 and 1.00