select *
from {{ ref('int_analysis_parameters') }}
where
    baseline_start_date <> date '1991-01-01'
    or baseline_end_date <> date '2020-12-31'
    or recent_start_date <> date '2021-01-01'
    or recent_end_date <> date '2025-12-31'
    or overall_completeness_threshold <> 0.80
    or monthly_completeness_threshold <> 0.70

union all

select *
from {{ ref('int_analysis_parameters') }}
qualify count(*) over () <> 1