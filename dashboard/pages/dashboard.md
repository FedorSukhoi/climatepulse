---
title: ClimatePulse | Temperature anomalies
---

## Temperature anomalies in the covered EU countries, 2021–2025

> **Coverage boundary:** This analysis covers qualifying stations in **15 of the EU-27 countries**. It is an equal-weight average of the countries with an eligible station in each month. It is not a complete EU-27 temperature measure.

The comparison uses paired NOAA GHCN-Daily maximum and minimum temperatures, a fixed 1991–2020 baseline, and complete months through December 2025. An anomaly of +1 °C means a monthly station mean was 1 °C above that station's baseline for the same calendar month.

```sql summary
select
    round(avg(equal_weight_included_country_mean_anomaly_c), 2) as average_monthly_anomaly_c,
    min(included_country_count) as minimum_included_countries,
    max(included_country_count) as maximum_included_countries,
    count(*) as months,
    count(*) filter (where included_country_count < represented_country_universe_count) as partial_country_months
from climatepulse.agg_included_countries_monthly_anomalies
```

<Details title="How to read the series">
Each monthly value first averages eligible station anomalies within each country, then averages the available country means equally. A country with no eligible station in a month stays in the coverage data and is omitted from that month's mean. Missing anomalies are never treated as zero.
</Details>

## Included-country trend

```sql trend
select
    month_start,
    equal_weight_included_country_mean_anomaly_c as anomaly_c,
    included_country_count,
    eligible_contributing_station_count
from climatepulse.agg_included_countries_monthly_anomalies
order by month_start
```

<LineChart data={trend} x=month_start y=anomaly_c yAxisTitle="Anomaly (°C)" title="Monthly anomaly versus 1991–2020" echartsOptions={{xAxis: {max: '2025-12-31'}}}/>

The five-year mean of the 60 monthly included-country values is **0.94 °C**. The contributing-country count varies from **13 to 15**; **23 of 60 months** have fewer than all 15 represented countries. Inspect the coverage table below before comparing individual months.

```sql annual
select
    calendar_year,
    round(avg(equal_weight_included_country_mean_anomaly_c), 3) as mean_monthly_anomaly_c,
    min(included_country_count) as minimum_countries,
    max(included_country_count) as maximum_countries
from climatepulse.agg_included_countries_monthly_anomalies
group by calendar_year
order by calendar_year
```

<BarChart data={annual} x=calendar_year y=mean_monthly_anomaly_c yAxisTitle="Mean monthly anomaly (°C)" title="Annual summary of the monthly series"/>

These annual values are simple averages of the 12 monthly aggregate values, with coverage varying by month. They are descriptive summaries of this station sample, not spatially complete national or EU averages.

## Compare countries

```sql country_summary
select
    country_name,
    round(avg(country_mean_temperature_anomaly_c), 2) as mean_monthly_anomaly_c,
    max(total_final_stations) as final_stations,
    count(country_mean_temperature_anomaly_c) as eligible_months,
    min(eligible_contributing_stations) as minimum_contributors
from climatepulse.agg_country_monthly_anomalies
group by country_name
order by mean_monthly_anomaly_c desc
```

<BarChart data={country_summary} x=country_name y=mean_monthly_anomaly_c swapXY=true yAxisTitle="Mean monthly anomaly (°C)" title="Country monthly means, averaged over eligible months"/>

<DataTable data={country_summary} rows=15/>

Country bars have unequal evidence behind them. Bulgaria, Croatia, Luxembourg, and Slovenia have one final station each; a single missing station-month removes that country's contribution. Germany has 277 stations and Sweden has 100, but each available country mean receives one equal weight in the aggregate.

## Country and station detail

Select two to four countries to compare their monthly series. You can also choose one country or use **Select all** in the menu. The table below each chart shows the number of eligible stations behind every country-month value.

```sql country_options
select distinct country_name from climatepulse.dim_locations order by country_name
```

<Dropdown data={country_options} name=country value=country_name multiple defaultValue={['France', 'Germany', 'Sweden']} title="Countries to compare"/>

```sql selected_country
select
    month_start,
    country_name,
    country_mean_temperature_anomaly_c as anomaly_c,
    eligible_contributing_stations,
    total_final_stations,
    station_contribution_ratio
from climatepulse.agg_country_monthly_anomalies
where country_name in ${inputs.country.value}
order by month_start, country_name
```

<LineChart data={selected_country} x=month_start y=anomaly_c series=country_name yAxisTitle="Anomaly (°C)" title="Country series" echartsOptions={{xAxis: {max: '2025-12-31'}}}/>

<DataTable data={selected_country} rows=12/>

```sql selected_stations
select
    locations.station_id,
    locations.station_name,
    locations.country_name,
    count(*) filter (where facts.is_anomaly_eligible) as eligible_months,
    round(avg(facts.temperature_anomaly_c), 2) as mean_eligible_anomaly_c
from climatepulse.dim_locations as locations
join climatepulse.fct_anomalies as facts using (station_id)
where locations.country_name in ${inputs.country.value}
group by locations.station_id, locations.station_name, locations.country_name
order by locations.country_name, locations.station_name
```

<DataTable data={selected_stations} rows=15/>

## Coverage and missingness

```sql coverage
select
    month_start,
    included_country_count,
    represented_country_universe_count,
    eligible_contributing_station_count,
    represented_station_universe_count,
    station_contribution_ratio as station_participation_pct,
    eu27_target_country_coverage_ratio as eu27_country_participation_pct
from climatepulse.agg_included_countries_monthly_anomalies
order by month_start
```

<LineChart data={coverage} x=month_start y=included_country_count yAxisTitle="Countries" title="Countries included each month" echartsOptions={{xAxis: {max: '2025-12-31'}}}/>

<DataTable data={coverage} rows=12/>

The EU-27 participation percentage is the share of target countries with at least one eligible anomaly, not a share of Europe's land area or population. Station participation uses the frozen 640-station universe as its denominator.

## Method and limits

1. Retain only unflagged NOAA `TMAX` and `TMIN` readings, converting tenths of °C to °C.
2. Pair valid maximum and minimum readings by station-day; take their mean. Exclude days without both.
3. Require at least 70% paired days for an eligible station-year-month. Average the eligible 1991–2020 year-month means with equal year weight.
4. Require at least 21 eligible baseline years for that station and calendar month, and at least 70% paired days in the recent month.
5. Average eligible station anomalies within a country, then average available country means equally. Keep missing station and country grid rows for coverage diagnostics.

The frozen 640 stations represent 15 countries. Twelve EU members have no qualifying stations. Stations are unevenly distributed, and the country-first method gives a one-station country the same country weight as a station-rich country when it contributes. The raw NOAA snapshot and its manifest are required to reproduce the complete pipeline; this dashboard instead ships validated mart exports. The full source and model contracts are documented in the repository.
