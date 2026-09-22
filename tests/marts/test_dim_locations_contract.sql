with locations as (

    select *

    from {{ ref('dim_locations') }}

),

invalid_rows as (

    select
        station_id,
        'invalid location attributes' as violation

    from locations

    where
        latitude is null
        or latitude not between -90 and 90
        or longitude is null
        or longitude not between -180 and 180
        or baseline_completeness not between 0 and 1
        or recent_completeness not between 0 and 1
        or baseline_min_monthly_completeness not between 0 and 1
        or recent_min_monthly_completeness not between 0 and 1

),

summary_metrics as (

    select
        count(*) as row_count,
        count(distinct noaa_country_code) as noaa_country_count,
        count(distinct iso_alpha2) as iso_country_count,
        count(distinct country_name) as country_name_count

    from locations

),

invalid_summary as (

    select
        cast(null as varchar) as station_id,
        'unexpected station or country count' as violation

    from summary_metrics

    where
        row_count <> (select count(*) from {{ ref('stg_noaa__stations') }})
        or noaa_country_count <> (select count(distinct noaa_country_code) from {{ ref('stg_noaa__stations') }})
        or iso_country_count <> (select count(distinct iso_alpha2) from {{ ref('stg_noaa__stations') }})
        or country_name_count <> (select count(distinct country_name) from {{ ref('stg_noaa__stations') }})

)

select * from invalid_rows

union all

select * from invalid_summary