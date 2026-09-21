# Mart contracts

## Purpose

The ClimatePulse marts provide stable, tested analytical tables for
downstream reporting and the Evidence data product.

The marts publish methodology established in the staging and intermediate
layers. They do not redefine station eligibility, monthly completeness,
baseline coverage, or anomaly calculations.

All complete-period mart outputs cover January 2021 through December 2025.
No 2026 observations are included.

## Model summary

| Model | Grain | Expected rows |
|---|---|---:|
| `dim_locations` | One final station | 640 |
| `fct_anomalies` | One final station and recent-period month | 38,400 |
| `agg_country_monthly_anomalies` | One represented country and recent-period month | 900 |
| `agg_included_countries_monthly_anomalies` | One recent-period month | 60 |

## `dim_locations`

`dim_locations` contains the frozen analytical station universe.

It includes:

- Station identity and name.
- NOAA and ISO country identifiers.
- Country name.
- Latitude, longitude, and elevation.
- Baseline and recent-period station-selection completeness metrics.

The dimension contains 640 stations across 15 represented EU countries.

The completeness fields describe the station-selection evidence. They are
not monthly contribution measures and must not be used as substitutes for
the month-specific coverage fields in the aggregate marts.

Source provenance fields are intentionally excluded because they belong to
the ingestion and staging layers rather than the reporting interface.

## `fct_anomalies`

`fct_anomalies` preserves the complete 640-station by 60-month recent-period
grid.

A row is anomaly-eligible only when:

1. The recent station-month passes the frozen monthly completeness rule.
2. The corresponding station and calendar-month baseline passes the
   baseline-year coverage rule.

Eligible anomalies are calculated as:

`monthly mean temperature - baseline mean temperature`

Ineligible station-months remain present with a null anomaly. They are not
dropped, converted to zero, or imputed.

For the frozen source snapshot:

- Total station-months: 38,400.
- Eligible anomalies: 38,157.
- Ineligible and null anomalies: 243.

These counts reconcile the current snapshot; they are not general
methodological constants.

## Country-month aggregation

`agg_country_monthly_anomalies` aggregates eligible station anomalies within
each represented country and month.

Every country-month retains:

- The total number of final stations in the country.
- The number of eligible contributing stations.
- The station contribution ratio.
- Whether at least one station contributes.
- The mean of eligible station anomalies.

A country-month mean is available when at least one station has an eligible
anomaly. No additional country-level percentage threshold is imposed.

This decision avoids introducing an unsupported threshold after station
selection. It also avoids rules with inconsistent practical effects across
countries: Germany has 277 final stations, while Bulgaria, Croatia,
Luxembourg, and Slovenia each have one.

The coverage fields must accompany country results because a value based on
one contributing station is not equivalent in spatial support to a value
based on hundreds of stations.

For the frozen source snapshot:

- Country-month rows: 900.
- Country-months with partial station participation: 153.
- Country-months with no eligible contributor: 35.
- Country-months with no eligible contributor retain a null country mean.

## Included-country aggregation

`agg_included_countries_monthly_anomalies` first calculates country-month
means and then averages the available country means with equal country
weight.

The calculation is conceptually:

`sum of available country means / included country count`

It is not:

`sum of eligible station anomalies / eligible station count`

This country-first calculation prevents station-rich countries from
dominating solely because they contain more NOAA stations. Germany and
Sweden account for 377 of the 640 final stations, so direct station weighting
would heavily favor their observations.

The aggregate includes explicit diagnostics:

- Eligible contributing station count.
- Represented station universe count.
- Station contribution ratio.
- Included-country count.
- Represented-country universe count.
- EU-27 target-country count.
- Coverage ratio against the 15 represented countries.
- Coverage ratio against the EU-27 target.

Station contribution counts are diagnostic only. They do not determine the
country weights.

For the frozen source snapshot:

- Included-country monthly rows: 60.
- Included countries per month range from 13 to 15.
- Twenty-three months contain fewer than all 15 represented countries.
- Direct station weighting and country-first weighting differ by more than
  0.01 degrees Celsius in 59 of 60 months.
- Their maximum absolute monthly difference is approximately 0.698 degrees
  Celsius.
- Their mean absolute monthly difference is approximately 0.264 degrees
  Celsius.

## Geographic interpretation

The target geography is the EU-27, but qualifying station coverage exists
for only 15 member states.

The aggregate therefore represents the available portion of the qualifying
15-country station universe. It must not be labelled as:

- An EU-27 anomaly.
- A complete European anomaly.
- A population-weighted European temperature measure.
- An area-weighted European temperature measure.

Equal country weighting addresses unequal station counts, but it creates a
different limitation: a country represented by one station can receive the
same country-level weight as a country represented by hundreds of stations.

This tradeoff is deliberate and must remain visible through station and
country contribution metrics.

## Missingness rules

Across all marts:

- Ineligible anomalies remain null.
- Missing values are never interpreted as zero.
- Missing country-month means are excluded from the included-country
  denominator.
- No missing station, country, or monthly value is imputed.
- Complete grids are retained wherever the analytical universe defines
  them.

## Test strategy

Mart tests protect:

- Model grains and expected grid dimensions.
- Station and country relationships.
- Coordinate and completeness ranges.
- Eligibility and null equivalence.
- Anomaly arithmetic.
- Station-count reconciliation.
- Country-month aggregation.
- Country-first equal weighting.
- Frozen-snapshot row and coverage counts.
- Exclusion of 2026 from complete-period outputs.

Snapshot reconciliation tests are named explicitly so that fixed observed
counts are not confused with permanent business rules.