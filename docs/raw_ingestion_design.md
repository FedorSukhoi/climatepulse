# ClimatePulse raw ingestion design

## Purpose

This document defines how ClimatePulse ingests NOAA GHCN-Daily station
files into DuckDB and establishes the boundary between raw ingestion and
dbt transformation.

## Architecture decision

ClimatePulse materializes the required NOAA records into DuckDB instead
of exposing the compressed CSV files as a permanent external view.

The source snapshot contains 971 compressed station files totaling
approximately 0.348 GiB. DuckDB can scan the files quickly, but an
the raw records avoids repeated gzip decompression during dbt development
and downstream testing.

Ingestion is implemented by:

`python scripts/ingest_noaa_to_duckdb.py`

The script performs a transactional full refresh. If ingestion or
validation fails, the transaction is rolled back rather than leaving
partially refreshed raw tables.

## Input scope

The ingestion process reads all 971 downloaded metadata-qualified
candidate-station files.

It does not restrict ingestion to the final 640 analytical stations.
Station eligibility is an analytical rule and must be applied downstream.

Only the following NOAA elements are materialized:

- `TMAX`
- `TMIN`

This is a source-scope restriction because ClimatePulse is explicitly a
temperature analytics project.

The current source snapshot contains:

- 46,281,772 temperature element-day rows
- 23,236,784 TMAX rows
- 23,044,988 TMIN rows
- 971 stations
- Dates from 1824-01-01 through 2026-08-26
- 40,684 rows with a nonblank NOAA quality flag

These figures describe the current snapshot and may change after a
deliberate source refresh.

## Raw relations

### `raw.noaa_daily_observations`

Grain:

One NOAA station, observation date, and temperature element.

Columns:

- `station_id`
- `observation_date`
- `element`
- `data_value`
- `measurement_flag`
- `quality_flag`
- `source_flag`
- `observation_time`
- `source_file`
- `ingested_at_utc`

The raw table performs structural parsing only. It does not:

- Reject nonblank quality flags
- Convert tenths of degrees Celsius into degrees Celsius
- Calculate daily mean temperature
- Pair TMAX and TMIN records
- Apply station-eligibility rules
- Apply baseline or recent-period filters
- Remove 2026 observations

These responsibilities belong to the dbt staging and downstream layers.

### `raw.noaa_file_manifest`

Grain:

One compressed NOAA station file in the ingestion snapshot.

The manifest records:

- Station ID
- Source filename
- Compressed byte size
- SHA-256 checksum
- UTC ingestion timestamp
- Materialized temperature-row count
- Minimum observation date
- Maximum observation date

A tracked copy is written to:

`data/manifests/noaa_station_files_manifest.csv`

The manifest identifies and verifies the exact local source snapshot.
It detects upstream changes but cannot recover an old snapshot after its
raw files are deleted. Exact historical reconstruction would require
archiving the original source files in immutable storage, which is
outside the current local portfolio architecture.

## DuckDB and dbt boundary

The Python ingestion script owns the creation of the raw relations.

dbt declares those relations using:

- `source('noaa', 'daily_observations')`
- `source('noaa', 'file_manifest')`

dbt does not own or rebuild the raw tables. It tests them and uses them
as the entry point to the transformation graph.

The DuckDB and dbt sessions use UTC for timestamp consistency.

## Refresh procedure

Activate the project environment and run:

```bash
source .venv/bin/activate
python scripts/ingest_noaa_to_duckdb.py
dbt test --profiles-dir . --select "source:noaa+"