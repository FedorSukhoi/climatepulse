from pathlib import Path
from datetime import date
from collections import defaultdict
import csv
import gzip


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data/processed/eu27_candidate_stations.csv"
)

STATION_DIR = (
    PROJECT_ROOT
    / "data/raw/ghcn_daily/stations"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data/processed/station_completeness.csv"
)


BASELINE_START = date(1991, 1, 1)
BASELINE_END = date(2020, 12, 31)

RECENT_START = date(2021, 1, 1)
RECENT_END = date(2025, 12, 31)


def days_inclusive(start_date, end_date):
    return (end_date - start_date).days + 1


BASELINE_EXPECTED_DAYS = days_inclusive(
    BASELINE_START,
    BASELINE_END,
)

RECENT_EXPECTED_DAYS = days_inclusive(
    RECENT_START,
    RECENT_END,
)


def load_candidates():
    stations = {}

    with CANDIDATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            stations[row["station_id"]] = row

    return stations


def parse_noaa_date(raw_date):
    return date(
        int(raw_date[0:4]),
        int(raw_date[4:6]),
        int(raw_date[6:8]),
    )


def valid_temperature_value(raw_value):
    try:
        value = int(raw_value)
    except ValueError:
        return False

    return value != -9999


def evaluate_station(filepath):
    baseline_dates = {
        "TMAX": set(),
        "TMIN": set(),
    }

    recent_dates = {
        "TMAX": set(),
        "TMIN": set(),
    }

    flagged_rows = 0
    invalid_value_rows = 0

    with gzip.open(
        filepath,
        mode="rt",
        encoding="utf-8",
    ) as file:

        reader = csv.reader(file)

        for row in reader:
            raw_date = row[1]
            element = row[2]
            raw_value = row[3]
            quality_flag = row[5]

            if element not in {"TMAX", "TMIN"}:
                continue

            observation_date = parse_noaa_date(
                raw_date
            )

            if (
                observation_date < BASELINE_START
                or observation_date > RECENT_END
            ):
                continue

            if quality_flag:
                flagged_rows += 1
                continue

            if not valid_temperature_value(raw_value):
                invalid_value_rows += 1
                continue

            if (
                BASELINE_START
                <= observation_date
                <= BASELINE_END
            ):
                baseline_dates[element].add(
                    observation_date
                )

            elif (
                RECENT_START
                <= observation_date
                <= RECENT_END
            ):
                recent_dates[element].add(
                    observation_date
                )

    baseline_paired = (
        baseline_dates["TMAX"]
        & baseline_dates["TMIN"]
    )

    recent_paired = (
        recent_dates["TMAX"]
        & recent_dates["TMIN"]
    )

    baseline_count = len(baseline_paired)
    recent_count = len(recent_paired)

    return {
        "baseline_valid_days": baseline_count,
        "baseline_expected_days": BASELINE_EXPECTED_DAYS,
        "baseline_completeness": (
            baseline_count
            / BASELINE_EXPECTED_DAYS
        ),
        "recent_valid_days": recent_count,
        "recent_expected_days": RECENT_EXPECTED_DAYS,
        "recent_completeness": (
            recent_count
            / RECENT_EXPECTED_DAYS
        ),
        "flagged_temperature_rows": flagged_rows,
        "invalid_temperature_rows": invalid_value_rows,
    }


def write_results(results):
    fieldnames = [
        "station_id",
        "country_name",
        "iso_alpha2",
        "station_name",
        "baseline_valid_days",
        "baseline_expected_days",
        "baseline_completeness",
        "recent_valid_days",
        "recent_expected_days",
        "recent_completeness",
        "flagged_temperature_rows",
        "invalid_temperature_rows",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


def main():
    candidates = load_candidates()

    results = []

    print(
        "Expected baseline days:",
        BASELINE_EXPECTED_DAYS,
    )

    print(
        "Expected recent days:",
        RECENT_EXPECTED_DAYS,
    )

    print()

    total = len(candidates)

    for index, (
        station_id,
        station,
    ) in enumerate(
        candidates.items(),
        start=1,
    ):

        filepath = (
            STATION_DIR
            / f"{station_id}.csv.gz"
        )

        if not filepath.exists():
            print(
                f"Missing file: {station_id}"
            )
            continue

        result = evaluate_station(filepath)

        results.append(
            {
                "station_id": station_id,
                "country_name": station[
                    "country_name"
                ],
                "iso_alpha2": station[
                    "iso_alpha2"
                ],
                "station_name": station[
                    "station_name"
                ],
                **result,
            }
        )

        if index % 100 == 0:
            print(
                f"Evaluated "
                f"{index}/{total}"
            )

    write_results(results)

    print()
    print(
        f"Stations evaluated: "
        f"{len(results)}"
    )

    print(
        f"Results written to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()