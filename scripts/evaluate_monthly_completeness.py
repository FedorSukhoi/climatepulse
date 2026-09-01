from pathlib import Path
from datetime import date
from collections import defaultdict
import csv
import gzip


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data/processed/station_completeness.csv"
)

STATION_DIR = (
    PROJECT_ROOT
    / "data/raw/ghcn_daily/stations"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data/processed/monthly_completeness.csv"
)


BASELINE_START = date(1991, 1, 1)
BASELINE_END = date(2020, 12, 31)

RECENT_START = date(2021, 1, 1)
RECENT_END = date(2025, 12, 31)


def parse_date(raw_date):
    return date(
        int(raw_date[0:4]),
        int(raw_date[4:6]),
        int(raw_date[6:8]),
    )


def valid_temperature_value(raw_value):
    try:
        return int(raw_value) != -9999
    except ValueError:
        return False


def expected_days_by_month(start_date, end_date):
    counts = defaultdict(int)

    current = start_date

    while current <= end_date:
        counts[current.month] += 1

        current = date.fromordinal(
            current.toordinal() + 1
        )

    return counts


BASELINE_EXPECTED = expected_days_by_month(
    BASELINE_START,
    BASELINE_END,
)

RECENT_EXPECTED = expected_days_by_month(
    RECENT_START,
    RECENT_END,
)


def load_candidates():
    with CANDIDATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        return {
            row["station_id"]: row
            for row in csv.DictReader(file)
        }


def evaluate_station(filepath):
    observations = {
        "baseline": {
            "TMAX": defaultdict(set),
            "TMIN": defaultdict(set),
        },
        "recent": {
            "TMAX": defaultdict(set),
            "TMIN": defaultdict(set),
        },
    }

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

            if quality_flag:
                continue

            if not valid_temperature_value(raw_value):
                continue

            observation_date = parse_date(raw_date)

            if (
                BASELINE_START
                <= observation_date
                <= BASELINE_END
            ):
                period = "baseline"

            elif (
                RECENT_START
                <= observation_date
                <= RECENT_END
            ):
                period = "recent"

            else:
                continue

            observations[period][element][
                observation_date.month
            ].add(observation_date)

    result = {}

    for period, expected in (
        ("baseline", BASELINE_EXPECTED),
        ("recent", RECENT_EXPECTED),
    ):

        monthly_rates = []

        for month in range(1, 13):
            tmax_dates = (
                observations[period]["TMAX"][month]
            )

            tmin_dates = (
                observations[period]["TMIN"][month]
            )

            paired_dates = (
                tmax_dates & tmin_dates
            )

            completeness = (
                len(paired_dates)
                / expected[month]
            )

            result[
                f"{period}_month_{month:02d}"
            ] = completeness

            monthly_rates.append(completeness)

        result[
            f"{period}_minimum_monthly_completeness"
        ] = min(monthly_rates)

    return result


def main():
    candidates = load_candidates()

    results = []

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
            continue

        monthly = evaluate_station(filepath)

        results.append(
            {
                "station_id": station_id,
                "country_name": station["country_name"],
                "iso_alpha2": station["iso_alpha2"],
                "baseline_completeness":
                    station["baseline_completeness"],
                "recent_completeness":
                    station["recent_completeness"],
                **monthly,
            }
        )

        if index % 100 == 0:
            print(
                f"Evaluated {index}/{total}"
            )

    if not results:
        raise RuntimeError(
            "No monthly completeness results generated."
        )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print(
        f"Stations evaluated: {len(results)}"
    )

    print(
        f"Output written to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()