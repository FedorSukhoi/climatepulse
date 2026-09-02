from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize NOAA GHCN-Daily temperature records in DuckDB."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "data" / "climatepulse.duckdb",
    )
    parser.add_argument(
        "--stations-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / "ghcn_daily" / "stations",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=(
            PROJECT_ROOT
            / "data"
            / "manifests"
            / "noaa_station_files_manifest.csv"
        ),
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def sql_string(value: str) -> str:
    return value.replace("'", "''")


def write_manifest(
    path: Path,
    rows: list[tuple],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    headers = [
        "station_id",
        "source_file",
        "compressed_bytes",
        "sha256",
        "ingested_at_utc",
        "temperature_row_count",
        "min_observation_date",
        "max_observation_date",
    ]

    with temporary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)

    temporary_path.replace(path)


def main() -> None:
    args = parse_args()

    database_path = args.database.resolve()
    stations_dir = args.stations_dir.resolve()
    manifest_path = args.manifest.resolve()

    station_files = sorted(stations_dir.glob("*.csv.gz"))

    if not station_files:
        raise FileNotFoundError(
            f"No .csv.gz files found under {stations_dir}"
        )

    database_path.parent.mkdir(parents=True, exist_ok=True)

    ingested_at = datetime.now(timezone.utc).replace(microsecond=0)
    ingested_at_text = ingested_at.isoformat()

    print(f"Hashing {len(station_files):,} source files...")

    manifest_input = [
        (
            path.name.removesuffix(".csv.gz"),
            path.name,
            path.stat().st_size,
            sha256_file(path),
        )
        for path in station_files
    ]

    csv_glob = sql_string(
        (stations_dir / "*.csv.gz").as_posix()
    )
    timestamp_literal = sql_string(ingested_at_text)

    with duckdb.connect(str(database_path)) as connection:
        connection.execute("set timezone = 'UTC'")
        
        try:
            connection.execute("begin transaction")
            connection.execute("create schema if not exists raw")

            print("Materializing raw.noaa_daily_observations...")

            connection.execute(
                f"""
                create or replace table raw.noaa_daily_observations as
                select
                    station_id,
                    strptime(
                        observation_date_raw,
                        '%Y%m%d'
                    )::date as observation_date,
                    element,
                    data_value,
                    measurement_flag,
                    quality_flag,
                    source_flag,
                    observation_time,
                    regexp_extract(
                        source_path,
                        '([^/]+)$',
                        1
                    ) as source_file,
                    timestamptz '{timestamp_literal}'
                        as ingested_at_utc
                from read_csv(
                    '{csv_glob}',
                    auto_detect = false,
                    header = false,
                    delim = ',',
                    nullstr = '',
                    filename = 'source_path',
                    columns = {{
                        'station_id': 'varchar',
                        'observation_date_raw': 'varchar',
                        'element': 'varchar',
                        'data_value': 'integer',
                        'measurement_flag': 'varchar',
                        'quality_flag': 'varchar',
                        'source_flag': 'varchar',
                        'observation_time': 'varchar'
                    }}
                )
                where element in ('TMAX', 'TMIN')
                """
            )

            connection.execute(
                """
                create or replace temp table noaa_manifest_input (
                    station_id varchar,
                    source_file varchar,
                    compressed_bytes bigint,
                    sha256 varchar
                )
                """
            )

            connection.executemany(
                """
                insert into noaa_manifest_input
                values (?, ?, ?, ?)
                """,
                manifest_input,
            )

            connection.execute(
                f"""
                create or replace table raw.noaa_file_manifest as
                with observation_statistics as (
                    select
                        source_file,
                        count(*) as temperature_row_count,
                        min(observation_date) as min_observation_date,
                        max(observation_date) as max_observation_date
                    from raw.noaa_daily_observations
                    group by source_file
                )

                select
                    manifest.station_id,
                    manifest.source_file,
                    manifest.compressed_bytes,
                    manifest.sha256,
                    timestamptz '{timestamp_literal}'
                        as ingested_at_utc,
                    coalesce(
                        statistics.temperature_row_count,
                        0
                    ) as temperature_row_count,
                    statistics.min_observation_date,
                    statistics.max_observation_date
                from noaa_manifest_input as manifest
                left join observation_statistics as statistics
                    using (source_file)
                """
            )

            summary = connection.execute(
                """
                select
                    count(*) as temperature_rows,
                    count(distinct station_id) as station_count,
                    count(distinct source_file) as source_file_count,
                    min(observation_date) as minimum_date,
                    max(observation_date) as maximum_date,
                    count_if(element = 'TMAX') as tmax_rows,
                    count_if(element = 'TMIN') as tmin_rows,
                    count_if(quality_flag is not null)
                        as quality_flagged_rows
                from raw.noaa_daily_observations
                """
            ).fetchone()

            manifest_count = connection.execute(
                """
                select count(*)
                from raw.noaa_file_manifest
                """
            ).fetchone()[0]

            if summary[1] != len(station_files):
                raise RuntimeError(
                    "Materialized station count does not match source files: "
                    f"{summary[1]} != {len(station_files)}"
                )

            if summary[2] != len(station_files):
                raise RuntimeError(
                    "Materialized source-file count does not match input: "
                    f"{summary[2]} != {len(station_files)}"
                )

            if manifest_count != len(station_files):
                raise RuntimeError(
                    "Manifest count does not match source files: "
                    f"{manifest_count} != {len(station_files)}"
                )

            connection.execute("commit")

        except Exception:
            connection.execute("rollback")
            raise

        manifest_rows = connection.execute(
            """
            select
                station_id,
                source_file,
                compressed_bytes,
                sha256,
                ingested_at_utc,
                temperature_row_count,
                min_observation_date,
                max_observation_date
            from raw.noaa_file_manifest
            order by station_id
            """
        ).fetchall()

    write_manifest(manifest_path, manifest_rows)

    labels = [
        "temperature_rows",
        "station_count",
        "source_file_count",
        "minimum_date",
        "maximum_date",
        "tmax_rows",
        "tmin_rows",
        "quality_flagged_rows",
    ]

    print("\nIngestion complete:")
    for label, value in zip(labels, summary):
        print(f"{label}: {value:,}" if isinstance(value, int) else f"{label}: {value}")

    print(f"manifest_rows: {manifest_count:,}")
    print(f"database: {database_path}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()