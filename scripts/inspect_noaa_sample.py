from pathlib import Path
from collections import Counter
import csv
import gzip


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SAMPLE_DIR = (
    PROJECT_ROOT
    / "data/raw/ghcn_daily/sample"
)


def inspect_file(filepath):
    element_counts = Counter()
    quality_flags = Counter()

    temperature_rows = 0

    earliest_date = None
    latest_date = None

    with gzip.open(
        filepath,
        mode="rt",
        encoding="utf-8",
    ) as file:

        reader = csv.reader(file)

        for row in reader:
            station_id = row[0]
            date = row[1]
            element = row[2]
            quality_flag = row[5]

            element_counts[element] += 1

            if element not in {"TMAX", "TMIN"}:
                continue

            temperature_rows += 1

            if earliest_date is None or date < earliest_date:
                earliest_date = date

            if latest_date is None or date > latest_date:
                latest_date = date

            quality_flags[
                quality_flag if quality_flag else "BLANK"
            ] += 1

    print("=" * 70)
    print(filepath.name)
    print(f"Station ID: {station_id}")
    print(f"Temperature rows: {temperature_rows}")
    print(
        f"Temperature date range: "
        f"{earliest_date} → {latest_date}"
    )

    print()
    print("TMAX/TMIN counts:")

    for element in ("TMAX", "TMIN"):
        print(
            f"  {element}: "
            f"{element_counts[element]}"
        )

    print()
    print("Temperature quality flags:")

    for flag, count in sorted(quality_flags.items()):
        print(f"  {flag}: {count}")


def main():
    files = sorted(SAMPLE_DIR.glob("*.csv.gz"))

    if not files:
        raise RuntimeError(
            "No sample files found. "
            "Run download_noaa_sample.py first."
        )

    for filepath in files:
        inspect_file(filepath)


if __name__ == "__main__":
    main()