"""Create a deterministic, isolated DuckDB fixture for dbt CI."""
from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "climatepulse_ci.duckdb"
STAMP = datetime(2025, 12, 31, tzinfo=timezone.utc)
STATIONS = (
    ("GM000000001", "GM", "DE", "Germany", "Fixture Germany A", 50.0, 8.0, 100.0),
    ("GM000000002", "GM", "DE", "Germany", "Fixture Germany B", 52.0, 9.0, 80.0),
    ("AU000000001", "AU", "AT", "Austria", "Fixture Austria", 48.0, 16.0, 200.0),
)


def days(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def observation_rows():
    for station_id, *_ in STATIONS:
        for day in days(date(1991, 1, 1), date(2026, 1, 2)):
            # The baseline January coverage is exactly 20 years for Germany B
            # and 21 years for Austria; all other baseline months are complete.
            if day.year <= 2020 and day.month == 1:
                if station_id == "GM000000002" and day.year > 2010:
                    continue
                if station_id == "AU000000001" and day.year > 2011:
                    continue
            # Austria has an empty recent month. The two German January 2022
            # months straddle the 70% threshold: 21/31 and 22/31 pairs.
            if day == date(2021, 1, 1) or (day.year == 2021 and day.month == 1):
                if station_id == "AU000000001":
                    continue
            if day.year == 2022 and day.month == 1:
                if station_id == "GM000000001" and day.day > 21:
                    continue
                if station_id == "GM000000002" and day.day > 22:
                    continue
            offset = 0 if day.year <= 2020 else {"GM000000001": 10, "GM000000002": 30, "AU000000001": 80}[station_id]
            for element, value in (("TMAX", 200 + offset), ("TMIN", 100 + offset)):
                flag = None
                # Exercise quality flags, sentinels, and missing pairs.
                if station_id == "GM000000002" and day == date(2021, 3, 1) and element == "TMAX":
                    flag = "X"
                if station_id == "GM000000002" and day == date(2021, 3, 2) and element == "TMIN":
                    value = -9999
                if station_id == "GM000000002" and day == date(2021, 3, 3) and element == "TMIN":
                    continue
                if station_id == "GM000000002" and day == date(2021, 3, 4) and element == "TMAX":
                    continue
                yield (station_id, day, element, value, None, flag, None, None, f"{station_id}.csv.gz", STAMP)


def main():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    # Only the explicitly named CI database is replaced.
    DATABASE.unlink(missing_ok=True)
    with TemporaryDirectory(prefix='climatepulse-fixture-') as directory:
        observations_csv = Path(directory) / 'observations.csv'
        with observations_csv.open('w', newline='') as f:
            writer = csv.writer(f)
            for row in observation_rows():
                writer.writerow([value.isoformat() if isinstance(value, (date, datetime)) else value for value in row])
        with duckdb.connect(str(DATABASE)) as con:
            load_fixture(con, observations_csv)


def load_fixture(con: duckdb.DuckDBPyConnection, observations_csv: Path):
    con.execute("set timezone = 'UTC'")
    con.execute("begin transaction")
    try:
        con.execute("create schema raw")
        con.execute("create table raw.noaa_daily_observations (station_id varchar, observation_date date, element varchar, data_value integer, measurement_flag varchar, quality_flag varchar, source_flag varchar, observation_time varchar, source_file varchar, ingested_at_utc timestamptz)")
        con.execute("copy raw.noaa_daily_observations from ? (header false, null '', dateformat '%Y-%m-%d', timestampformat '%Y-%m-%dT%H:%M:%S%z')", [str(observations_csv)])
        con.execute("create table raw.noaa_file_manifest as select station_id, source_file, 1::bigint as compressed_bytes, repeat('a', 64) as sha256, ?::timestamptz as ingested_at_utc, count(*)::bigint as temperature_row_count, min(observation_date) as min_observation_date, max(observation_date) as max_observation_date from raw.noaa_daily_observations group by station_id, source_file", [STAMP])
        con.execute("create table raw.final_stations (station_id varchar, noaa_country_code varchar, iso_alpha2 varchar, country_name varchar, station_name varchar, latitude double, longitude double, elevation_m double, baseline_completeness double, recent_completeness double, baseline_min_monthly_completeness double, recent_min_monthly_completeness double, source_file varchar, ingested_at_utc timestamptz)")
        con.executemany("insert into raw.final_stations values (?, ?, ?, ?, ?, ?, ?, ?, 0.95, 0.95, 0.75, 0.75, 'ci_fixture', ?)", [(*row, STAMP) for row in STATIONS])
        con.execute("create table raw.eu27_countries (noaa_country_code varchar, country_name varchar, iso_alpha2 varchar, source_file varchar, ingested_at_utc timestamptz)")
        with (ROOT / 'data/reference/eu27_countries.csv').open(newline='') as f:
            con.executemany("insert into raw.eu27_countries values (?, ?, ?, 'eu27_countries.csv', ?)", [(r['noaa_country_code'], r['country_name'], r['iso_alpha2'], STAMP) for r in csv.DictReader(f)])
        con.execute("create table raw.analysis_parameters (parameter varchar, value varchar, description varchar, source_file varchar, ingested_at_utc timestamptz)")
        with (ROOT / 'data/reference/analysis_parameters.csv').open(newline='') as f:
            con.executemany("insert into raw.analysis_parameters values (?, ?, ?, 'analysis_parameters.csv', ?)", [(r['parameter'], r['value'], r['description'], STAMP) for r in csv.DictReader(f)])
        checks = {
            'stations': ("select count(*) from raw.final_stations", 3),
            'countries': ("select count(*) from raw.eu27_countries", 27),
            'parameters': ("select count(*) from raw.analysis_parameters", 6),
            'manifest': ("select count(*) from raw.noaa_file_manifest", 3),
            'duplicates': ("select count(*) from (select station_id, observation_date, element from raw.noaa_daily_observations group by all having count(*) > 1)", 0),
        }
        for name, (query, expected) in checks.items():
            actual = con.execute(query).fetchone()[0]
            if actual != expected:
                raise ValueError(f'{name}: expected {expected}, got {actual}')
        con.execute('commit')
        print(f'Created deterministic CI fixture: {DATABASE}')
    except Exception:
        con.execute('rollback')
        raise

if __name__ == '__main__':
    main()
