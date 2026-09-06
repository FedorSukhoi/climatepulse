# ClimatePulse temperature-anomaly methodology

## Analytical scope

ClimatePulse calculates station-level monthly temperature anomalies for
the final analytical universe of 640 NOAA GHCN-Daily stations across
15 EU countries.

The analysis uses:

- Fixed baseline: 1991-01-01 through 2020-12-31
- Recent complete period: 2021-01-01 through 2025-12-31
- TMAX and TMIN only
- NOAA quality-approved observations
- No imputation of missing temperatures
- No 2026 observations in complete-period analysis

The project does not represent complete EU-27 observational coverage.

## Daily temperatures

A usable station-day requires both a valid TMAX and valid TMIN record.

Records are excluded when:

- The NOAA quality flag is nonblank
- The data value is a missing-value sentinel
- Either TMAX or TMIN is unavailable for the station-day

NOAA temperature values are converted from tenths of degrees Celsius
into degrees Celsius.

Canonical daily temperature is:

`daily_mean_temperature_c = (TMAX + TMIN) / 2`

The current snapshot contains 8,034,439 usable paired station-days from
1991 through 2025.

## Station-month temperatures

ClimatePulse constructs a complete grid of every final station and every
month from January 1991 through December 2025.

The grid contains:

- 640 stations
- 420 months
- 268,800 station-month rows

Monthly mean temperature is the arithmetic mean of all usable daily mean
temperatures within the station-month.

Each row records:

- Expected calendar days
- Usable paired days
- Monthly completeness
- Monthly mean temperature
- Whether monthly completeness reaches 70%

Empty station-months remain in the grid with zero paired days and a null
monthly mean. Missing months are not imputed or silently removed.

## Monthly completeness

A station-year-month is eligible for baseline or anomaly calculation
when:

`paired_day_count / expected_day_count >= 0.70`

This station-year-month rule is distinct from the earlier station
eligibility rules. It prevents a monthly mean based on only a handful of
days from receiving the same analytical weight as a well-observed month.

The current snapshot contains:

- 4,478 baseline station-months below 70%
- 228 recent station-months below 70%
- 3,568 completely empty station-months across the full grid

## Baseline construction

A separate climatological baseline is calculated for every station and
calendar month.

For each eligible baseline year, ClimatePulse first calculates the
station-year-month mean. It then averages those eligible annual monthly
means:

`baseline_mean(s, m) = mean(monthly_mean(s, y, m))`

This gives every eligible year equal weight. It prevents years with more
observed days from dominating the 30-year normal.

A station/calendar-month baseline requires at least 21 eligible years:

`minimum eligible years = ceil(30 × 0.70) = 21`

All 7,680 station/calendar-month baseline rows remain visible, including
rows that fail this rule. The current snapshot has four ineligible
baselines:

- `ROM00015280`, January: 19 eligible years
- `ROM00015280`, February: 19 eligible years
- `ROM00015280`, December: 19 eligible years
- `SWE00140712`, March: 18 eligible years

This rule does not remove either station from the frozen station
universe. It only prevents the affected station/calendar-month baseline
from supporting anomalies.

## Monthly anomalies

For an eligible recent station-month:

`temperature_anomaly_c = monthly_mean_temperature_c - baseline_mean_temperature_c`

An anomaly is eligible only when:

1. The recent station-month has at least 70% paired-day completeness.
2. The corresponding station/calendar-month baseline has at least
   21 eligible baseline years.

The complete recent grid contains:

- 38,400 station-month rows
- 38,157 eligible anomalies
- 243 ineligible/null anomalies

Ineligible rows remain present with explicit eligibility fields and a
null anomaly. This preserves missingness and coverage information for
downstream reporting.

## Geographic aggregation boundary

Checkpoint 9 does not aggregate station anomalies.

Country and regional aggregation belongs to the mart layer. Any
cross-country result must aggregate to country level before combining
countries so that Germany and Sweden do not dominate solely because
they have more qualifying stations.

Downstream outputs must expose contributing-station counts and included
country coverage.

## Reproducibility and validation

The methodology is implemented in the following dbt models:

- `int_analysis_parameters`
- `int_station_daily_temperatures`
- `int_station_monthly_temperatures`
- `int_station_monthly_baselines`
- `int_station_monthly_anomalies`

Validation includes:

- Typed parameter verification
- Unique station-day grain
- Daily mean arithmetic
- Complete station-month grid verification
- Monthly completeness reconciliation
- Unique station/calendar-month baselines
- Baseline coverage calculations
- Anomaly eligibility and arithmetic
- Source, staging, and intermediate relationship tests

Run the full validation suite with:

```bash
dbt test --profiles-dir .