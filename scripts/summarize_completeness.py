from pathlib import Path
from collections import defaultdict
import csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data/processed/station_completeness.csv"
)

THRESHOLDS = [
    0.70,
    0.80,
    0.90,
    0.95,
]


def load_rows():
    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        rows = list(csv.DictReader(file))

    for row in rows:
        row["baseline_completeness"] = float(
            row["baseline_completeness"]
        )

        row["recent_completeness"] = float(
            row["recent_completeness"]
        )

    return rows


def passes(row, threshold):
    return (
        row["baseline_completeness"]
        >= threshold
        and row["recent_completeness"]
        >= threshold
    )


def summarize_threshold(rows, threshold):
    passing = [
        row
        for row in rows
        if passes(row, threshold)
    ]

    countries = defaultdict(int)

    for row in passing:
        countries[row["country_name"]] += 1

    return passing, countries


def main():
    rows = load_rows()

    print(f"Stations evaluated: {len(rows)}")
    print()

    for threshold in THRESHOLDS:
        passing, countries = summarize_threshold(
            rows,
            threshold,
        )

        percentage = threshold * 100

        print("=" * 60)

        print(
            f"Threshold: {percentage:.0f}%"
        )

        print(
            f"Passing stations: "
            f"{len(passing)}"
        )

        print(
            f"Countries represented: "
            f"{len(countries)}"
        )

        missing_countries = (
            27 - len(countries)
        )

        print(
            f"EU countries missing: "
            f"{missing_countries}"
        )

        print()

        for country, count in sorted(
            countries.items()
        ):
            print(
                f"  {country:15} "
                f"{count}"
            )

        print()


if __name__ == "__main__":
    main()