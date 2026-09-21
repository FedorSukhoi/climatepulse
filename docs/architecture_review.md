# Analytical architecture review

## Review status

The ClimatePulse analytical architecture was reviewed after completion of
the anomaly marts.

Review outcome: accepted and frozen for dashboard and CI development.

No material correctness defect was identified. Future changes to grains,
eligibility rules, baseline methodology, geographic weighting, or
complete-period boundaries require an explicit methodology decision and
corresponding test and documentation updates.

## Layer responsibilities

### Raw layer

The raw DuckDB schema contains materialized source inputs:

- NOAA TMAX and TMIN element-day observations.
- NOAA file manifest metadata.
- The frozen final-station universe.
- EU-27 country reference data.
- Frozen analysis parameters.

The raw layer preserves source-oriented records and ingestion metadata. It
does not calculate analytical temperatures or anomalies.

### Staging layer

The staging layer standardizes individual raw sources.

Responsibilities include:

- Removing NOAA observations with nonblank quality flags.
- Removing missing-value sentinels.
- Converting NOAA tenths of degrees Celsius to degrees Celsius.
- Standardizing station, country, and parameter fields.
- Preserving source-level grains.

The staging layer does not pair TMAX and TMIN, calculate daily means,
construct monthly grids, calculate baselines, or aggregate countries.

### Intermediate layer

The intermediate layer implements the analytical methodology.

Responsibilities include:

- Typing the frozen analysis parameters.
- Restricting analysis to the final station universe and complete periods.
- Pairing valid TMAX and TMIN observations.
- Calculating canonical daily mean temperature.
- Constructing complete station-month grids.
- Measuring monthly completeness.
- Calculating equal-year-weighted station/calendar-month baselines.
- Enforcing the minimum eligible-baseline-year rule.
- Calculating recent-period station-month anomalies.
- Preserving eligibility and missingness.

These are analytical rules rather than source-cleaning rules, so they
correctly reside outside staging.

### Mart layer

The marts provide stable reporting interfaces.

Responsibilities include:

- Publishing the final station dimension.
- Publishing the complete station-month anomaly fact.
- Aggregating eligible station anomalies within countries.
- Aggregating available country means with equal country weight.
- Publishing station and country contribution diagnostics.
- Preserving nulls and complete analytical grids.

The marts do not redefine completeness, baseline, or anomaly methodology.

## Model grains

| Model | Grain | Expected rows |
|---|---|---:|
| `stg_noaa__observations` | Station, date, and element | Snapshot-dependent |
| `stg_noaa__stations` | Final station | 640 |
| `stg_reference__countries` | EU-27 country | 27 |
| `stg_reference__analysis_parameters` | Parameter | 6 |
| `int_analysis_parameters` | Typed parameter set | 1 |
| `int_station_daily_temperatures` | Station and calendar day | 8,034,439 |
| `int_station_monthly_temperatures` | Station and month, 1991–2025 | 268,800 |
| `int_station_monthly_baselines` | Station and calendar month | 7,680 |
| `int_station_monthly_anomalies` | Station and month, 2021–2025 | 38,400 |
| `dim_locations` | Final station | 640 |
| `fct_anomalies` | Final station and recent-period month | 38,400 |
| `agg_country_monthly_anomalies` | Represented country and recent-period month | 900 |
| `agg_included_countries_monthly_anomalies` | Recent-period month | 60 |

Model keys and grid dimensions are protected by generic and singular dbt
tests.

## Materialization strategy

Physical dbt relations are:

- Four staging views.
- One intermediate parameter view.
- Four intermediate analytical tables.
- Four mart tables.

The staging models remain views because they provide lightweight
standardization over materialized raw tables.

`int_analysis_parameters` explicitly overrides the intermediate folder
default and remains a view. It pivots six controlled parameter rows into one
typed row. Materializing this trivial transformation would not provide a
meaningful performance benefit.

The large analytical intermediate models are tables so that daily pairing,
complete-grid construction, and baseline calculations are not repeatedly
executed by downstream queries.

The marts are tables to provide stable and responsive dashboard-facing
relations.

There are no incremental models. A normal `dbt build` recreates the table
models, so an additional full-refresh mode is not required for current
materializations.

## Daily-temperature methodology

A usable station-day requires both a valid TMAX and a valid TMIN.

Canonical daily mean temperature is:

`(TMAX + TMIN) / 2`

NOAA TAVG is not used as the canonical measurement.

Days missing either component remain unusable. Missing measurements are not
imputed.

## Monthly completeness and missingness

The monthly model retains the complete station-month grid, including empty
months.

It records:

- Expected calendar days.
- Paired valid days.
- Monthly completeness.
- Monthly mean temperature.
- Completeness eligibility.

Missing temperatures and anomalies remain null. They are never converted to
zero.

This behavior propagates through the anomaly fact and aggregate marts.

## Baseline methodology

The baseline covers 1991 through 2020.

For each station, calendar month, and baseline year:

1. The station-year-month must meet the 70% paired-day completeness rule.
2. An eligible station-year-month mean is calculated.
3. Eligible yearly monthly means are averaged with equal year weight.

This prevents years with more valid daily observations from receiving
greater baseline weight.

A station/calendar-month baseline requires at least 21 eligible years:

`ceil(30 × 0.70) = 21`

All 7,680 station/calendar-month combinations remain present. Four fail the
coverage rule and are ineligible for anomaly use.

## Recent-period anomaly methodology

The complete recent period is January 2021 through December 2025.

A station-month anomaly is available only when:

- The recent station-month passes its monthly completeness rule.
- The station/calendar-month baseline passes its baseline coverage rule.

The anomaly is:

`monthly mean temperature - baseline mean temperature`

The complete fact contains 38,400 rows:

- 38,157 eligible anomalies.
- 243 ineligible and null anomalies.

No 2026 observations appear in complete-period marts.

## Geographic aggregation

Country means are calculated from eligible station anomalies within each
country-month.

No additional country-level station-percentage threshold is imposed. A
country mean is available when at least one eligible station contributes.

Every country-month exposes:

- Total final stations.
- Eligible contributing stations.
- Station contribution ratio.
- Country-value availability.
- Country mean anomaly.

The cross-country aggregate averages available country means with equal
country weight. It does not average all station anomalies directly.

This country-first rule materially affects results:

- Direct station weighting and country-first weighting differ by more than
  0.01 degrees Celsius in 59 of 60 months.
- Maximum observed absolute monthly difference is approximately 0.698
  degrees Celsius.
- Mean observed absolute monthly difference is approximately 0.264 degrees
  Celsius.

Country-first weighting is therefore a substantive methodological decision,
not merely a presentation choice.

## One-station countries

Bulgaria, Croatia, Luxembourg, and Slovenia each contain one final station.

When that station contributes, the country mean equals its anomaly and the
country receives the same cross-country weight as every other included
country.

This is an accepted tradeoff. Equal country weighting prevents
station-rich countries from dominating, but it does not make countries
equally well observed.

Station and country contribution counts must remain visible in reporting.

## Geographic scope and naming

The target geography is the EU-27, but final qualifying coverage exists for
only 15 member states.

The final aggregate is correctly named
`agg_included_countries_monthly_anomalies`.

It must not be described as:

- An EU-27 anomaly.
- A complete European anomaly.
- A population-weighted European temperature measure.
- An area-weighted European temperature measure.

Coverage ratios against both the represented 15-country universe and the
EU-27 target are published explicitly.

## Provenance and reproducibility

The NOAA checksum manifest detects source drift and records the ingested
snapshot.

The raw NOAA files and DuckDB database are excluded from Git because of
their size. Exact recovery of deleted historical NOAA bytes is not
guaranteed without immutable external raw-file storage.

A dbt build is reproducible from correctly materialized raw inputs, but it
does not itself recreate those raw inputs. End-to-end reconstruction also
requires the tracked ingestion and station-selection processes plus the
required NOAA source files.

This distinction must remain explicit in setup and reproduction
documentation.

## Test assessment

The complete project contains 219 passing data tests.

Testing responsibilities are separated as follows:

- Generic YAML tests protect simple column properties and relationships.
- Singular contract tests protect composite grains, cross-field rules,
  arithmetic, and grid dimensions.
- Reconciliation tests independently rebuild critical aggregations.
- Snapshot reconciliation tests protect frozen observed counts.

Some tests intentionally overlap at analytical boundaries. The overlap is
accepted where it protects a different failure mode. Exact snapshot counts
are named separately so they are not mistaken for permanent methodology.

## Operational assessment

Observed local build characteristics:

- Models: 5 views and 8 tables.
- Data tests: 219.
- Full dbt build time: approximately 9.06 seconds.
- DuckDB file size: approximately 372 MB.
- Incremental models: none.

These values are suitable for local analytical development.

The raw dataset remains too large for naive pull-request CI. CI must use a
small deterministic fixture rather than rebuilding the complete NOAA
snapshot.

## Accepted limitations

The frozen architecture accepts these limitations:

1. Only 15 of the 27 target EU countries have qualifying station coverage.
2. Station density is highly uneven across represented countries.
3. Four represented countries contain only one final station.
4. A country-month is published when at least one eligible station
   contributes; low-coverage values remain possible and are labelled.
5. Thirty-five country-months have no eligible station contributor.
6. Twenty-three recent months contain fewer than all 15 represented
   countries.
7. Station observations are not population-weighted or area-weighted.
8. Exact recovery of historical raw NOAA bytes requires storage outside the
   current Git repository.
9. Snapshot reconciliation tests require deliberate updates if the frozen
   source snapshot changes.
10. Data after 2025 is excluded from complete-period analysis.

## Freeze decision

The analytical architecture is approved for the next phases:

- Deterministic fixture design.
- Lightweight GitHub Actions CI.
- Evidence data-product development.

CI and dashboard code must consume these contracts rather than recreate or
silently reinterpret the methodology.