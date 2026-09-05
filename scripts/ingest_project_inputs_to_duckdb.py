from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PARAMETERS = {
    "baseline_start_date",
    "baseline_end_date",
    "recent_start_date",
    "recent_end_date",
    "overall_completeness_threshold",
    "monthly_completeness_threshold",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize ClimatePulse project inputs in DuckDB."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "data" / "climatepulse.duckdb",
    )
    parser.add_argument(
        "--final-stations",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "final_stations.csv",
    )
    parser.add_argument(
        "--countries",
        type=Path,
        default=PROJECT_ROOT / "data" / "reference" / "eu27_countries.csv",
    )
    parser.add_argument(
        "--parameters",
        type=Path,
        default=PROJECT_ROOT / "data" / "reference" / "analysis_parameters.csv",
    )
    return parser.parse_args()


def sql_string(value: str) -> str:
    return value.replace("'", "''")


def main() -> None:
    args = parse_args()

    database_path = args.database.resolve()
    final_stations_path = args.final_stations.resolve()
    countries_path = args.countries.resolve()
    parameters_path = args.parameters.resolve()

    input_paths = {
        "final stations": final_stations_path,
        "country reference": countries_path,
        "analysis parameters": parameters_path,
    }

    missing_inputs = [
        f"{name}: {path}"
        for name, path in input_paths.items()
        if not path.is_file()
    ]

    if missing_inputs:
        raise FileNotFoundError(
            "Required project inputs are missing:\n"
            + "\n".join(missing_inputs)
        )

    database_path.parent.mkdir(parents=True, exist_ok=True)

    ingested_at = datetime.now(timezone.utc).replace(microsecond=0)
    timestamp_literal = sql_string(ingested_at.isoformat())

    final_stations_sql_path = sql_string(final_stations_path.as_posix())
    countries_sql_path = sql_string(countries_path.as_posix())
    parameters_sql_path = sql_string(parameters_path.as_posix())

    with duckdb.connect(str(database_path)) as connection:
        connection.execute("set timezone = 'UTC'")

        try:
            connection.execute("begin transaction")
            connection.execute("create schema if not exists raw")

            connection.execute(
                f"""
                create or replace table raw.final_stations as
                select
                    station_id,
                    noaa_country_code,
                    iso_alpha2,
                    country_name,
                    station_name,
                    latitude,
                    longitude,
                    elevation_m,
                    baseline_completeness,
                    recent_completeness,
                    baseline_min_monthly_completeness,
                    recent_min_monthly_completeness,
                    '{final_stations_path.name}'::varchar
                        as source_file,
                    timestamptz '{timestamp_literal}'
                        as ingested_at_utc
                from read_csv(
                    '{final_stations_sql_path}',
                    auto_detect = false,
                    header = true,
                    nullstr = '',
                    columns = {{
                        'station_id': 'varchar',
                        'noaa_country_code': 'varchar',
                        'iso_alpha2': 'varchar',
                        'country_name': 'varchar',
                        'station_name': 'varchar',
                        'latitude': 'double',
                        'longitude': 'double',
                        'elevation_m': 'double',
                        'baseline_completeness': 'double',
                        'recent_completeness': 'double',
                        'baseline_min_monthly_completeness': 'double',
                        'recent_min_monthly_completeness': 'double'
                    }}
                )
                """
            )

            connection.execute(
                f"""
                create or replace table raw.eu27_countries as
                select
                    noaa_country_code,
                    country_name,
                    iso_alpha2,
                    '{countries_path.name}'::varchar as source_file,
                    timestamptz '{timestamp_literal}'
                        as ingested_at_utc
                from read_csv(
                    '{countries_sql_path}',
                    auto_detect = false,
                    header = true,
                    nullstr = '',
                    columns = {{
                        'noaa_country_code': 'varchar',
                        'country_name': 'varchar',
                        'iso_alpha2': 'varchar'
                    }}
                )
                """
            )

            connection.execute(
                f"""
                create or replace table raw.analysis_parameters as
                select
                    parameter,
                    value,
                    description,
                    '{parameters_path.name}'::varchar as source_file,
                    timestamptz '{timestamp_literal}'
                        as ingested_at_utc
                from read_csv(
                    '{parameters_sql_path}',
                    auto_detect = false,
                    header = true,
                    nullstr = '',
                    columns = {{
                        'parameter': 'varchar',
                        'value': 'varchar',
                        'description': 'varchar'
                    }}
                )
                """
            )

            final_station_summary = connection.execute(
                """
                select
                    count(*) as row_count,
                    count(distinct station_id) as station_count,
                    count(distinct iso_alpha2) as represented_countries
                from raw.final_stations
                """
            ).fetchone()

            country_summary = connection.execute(
                """
                select
                    count(*) as row_count,
                    count(distinct noaa_country_code) as noaa_code_count,
                    count(distinct iso_alpha2) as iso_code_count
                from raw.eu27_countries
                """
            ).fetchone()

            parameter_rows = connection.execute(
                """
                select parameter
                from raw.analysis_parameters
                """
            ).fetchall()
            actual_parameters = {row[0] for row in parameter_rows}

            unmatched_country_codes = connection.execute(
                """
                select count(*)
                from (
                    select distinct stations.noaa_country_code
                    from raw.final_stations as stations
                    where not exists (
                        select 1
                        from raw.eu27_countries as countries
                        where
                            countries.noaa_country_code
                            = stations.noaa_country_code
                    )
                )
                """
            ).fetchone()[0]

            if final_station_summary != (640, 640, 15):
                raise RuntimeError(
                    "Unexpected final-station summary: "
                    f"{final_station_summary}"
                )

            if country_summary != (27, 27, 27):
                raise RuntimeError(
                    "Unexpected EU country summary: "
                    f"{country_summary}"
                )

            if actual_parameters != EXPECTED_PARAMETERS:
                raise RuntimeError(
                    "Unexpected parameter set. "
                    f"Missing: {sorted(EXPECTED_PARAMETERS - actual_parameters)}; "
                    f"extra: {sorted(actual_parameters - EXPECTED_PARAMETERS)}"
                )

            if unmatched_country_codes != 0:
                raise RuntimeError(
                    "Final stations contain NOAA country codes "
                    "missing from the EU-27 reference."
                )

            connection.execute("commit")

        except Exception:
            connection.execute("rollback")
            raise

    print("Project-input ingestion complete")
    print(f"final_station_rows: {final_station_summary[0]:,}")
    print(f"final_station_ids: {final_station_summary[1]:,}")
    print(f"represented_countries: {final_station_summary[2]:,}")
    print(f"country_rows: {country_summary[0]:,}")
    print(f"noaa_country_codes: {country_summary[1]:,}")
    print(f"iso_country_codes: {country_summary[2]:,}")
    print(f"parameter_rows: {len(actual_parameters):,}")
    print(f"unmatched_country_codes: {unmatched_country_codes:,}")
    print(f"ingested_at_utc: {ingested_at.isoformat()}")
    print(f"database: {database_path}")


if __name__ == "__main__":
    main()