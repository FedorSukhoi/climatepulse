# NOAA GHCN-Daily Source Contract

## Source

NOAA Global Historical Climatology Network Daily (GHCN-Daily).

## Geographic Scope

EU-27 weather stations selected from NOAA station and inventory
metadata.

## Analytical Periods

Baseline:
1991-01-01 through 2020-12-31

Recent:
2021-01-01 through 2025-12-31

2026 data may later be treated separately as year-to-date /
provisional data.

## Required Elements

- TMAX
- TMIN

## Raw Units

TMAX and TMIN are stored by NOAA in tenths of degrees Celsius.

Example:

253 = 25.3 degrees Celsius

## Canonical Daily Temperature

ClimatePulse will calculate daily mean temperature as:

(TMAX + TMIN) / 2

rather than relying on NOAA TAVG.

## Quality Handling

Observations with a non-empty NOAA quality flag will be excluded
from canonical analytical temperature calculations.

The original quality flag will remain available in staging for
traceability.

## Missing Values

NOAA missing-value sentinels must be converted to NULL before
temperature calculations.

## Storage

Raw NOAA station files remain gzip-compressed and are not committed
to Git.

Generated or transformed observation files are also not committed
to Git.

## Station Eligibility

Initial metadata requirements:

- EU-27 country
- TMAX available
- TMIN available
- TMAX begins no later than 1991
- TMIN begins no later than 1991
- TMAX continues through at least 2021
- TMIN continues through at least 2021

Actual observation completeness will be evaluated separately.