from pathlib import Path
from collections import Counter
import csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MONTHLY_FILE = (
    PROJECT_ROOT
    / "data/processed/monthly_completeness.csv"
)

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data/processed/eu27_candidate_stations.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data/processed/final_stations.csv"
)


OVERALL_THRESHOLD = 0.80
MONTHLY_THRESHOLD = 0.70


def load_station_metadata():
    with CANDIDATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        return {
            row["station_id"]: row
            for row in csv.DictReader(file)
        }


def load_monthly_results():
    with MONTHLY_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        return list(csv.DictReader(file))


def qualifies(row):
    baseline = float(
        row["baseline_completeness"]
    )

    recent = float(
        row["recent_completeness"]
    )

    baseline_monthly = float(
        row[
            "baseline_minimum_monthly_completeness"
        ]
    )

    recent_monthly = float(
        row[
            "recent_minimum_monthly_completeness"
        ]
    )

    return (
        baseline >= OVERALL_THRESHOLD
        and recent >= OVERALL_THRESHOLD
        and baseline_monthly >= MONTHLY_THRESHOLD
        and recent_monthly >= MONTHLY_THRESHOLD
    )


def main():
    metadata = load_station_metadata()
    monthly_rows = load_monthly_results()

    final = []

    for row in monthly_rows:
        if not qualifies(row):
            continue

        station_id = row["station_id"]
        station = metadata[station_id]

        final.append(
            {
                "station_id": station_id,
                "noaa_country_code":
                    station["noaa_country_code"],
                "iso_alpha2":
                    station["iso_alpha2"],
                "country_name":
                    station["country_name"],
                "station_name":
                    station["station_name"],
                "latitude":
                    station["latitude"],
                "longitude":
                    station["longitude"],
                "elevation_m":
                    station["elevation_m"],
                "baseline_completeness":
                    row["baseline_completeness"],
                "recent_completeness":
                    row["recent_completeness"],
                "baseline_min_monthly_completeness":
                    row[
                        "baseline_minimum_monthly_completeness"
                    ],
                "recent_min_monthly_completeness":
                    row[
                        "recent_minimum_monthly_completeness"
                    ],
            }
        )

    fieldnames = final[0].keys()

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
        writer.writerows(final)

    counts = Counter(
        row["country_name"]
        for row in final
    )

    print(
        f"Final stations: {len(final)}"
    )

    print(
        f"Countries represented: {len(counts)}"
    )

    print()

    for country, count in sorted(counts.items()):
        print(
            f"{country:15} {count}"
        )


if __name__ == "__main__":
    main()