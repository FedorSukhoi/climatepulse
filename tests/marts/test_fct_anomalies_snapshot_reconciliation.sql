with anomaly_summary as (

    select
        count(*) as anomaly_rows,
        count(*) filter (
            where is_anomaly_eligible
        ) as eligible_anomalies,
        count(*) filter (
            where not is_anomaly_eligible
        ) as ineligible_anomalies,
        count(*) filter (
            where temperature_anomaly_c is null
        ) as null_anomalies

    from {{ ref('fct_anomalies') }}

)

select *

from anomaly_summary

where
    anomaly_rows <> 38400
    or eligible_anomalies <> 38157
    or ineligible_anomalies <> 243
    or null_anomalies <> 243