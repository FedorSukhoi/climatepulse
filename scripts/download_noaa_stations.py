from pathlib import Path
import csv
import time
import urllib.error
import urllib.request


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data/processed/eu27_candidate_stations.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data/raw/ghcn_daily/stations"
)

BASE_URL = (
    "https://www.ncei.noaa.gov/"
    "pub/data/ghcn/daily/by_station"
)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def load_candidates():
    with CANDIDATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def download_station(station):
    station_id = station["station_id"]

    filename = f"{station_id}.csv.gz"
    output_path = OUTPUT_DIR / filename

    if output_path.exists():
        return "skipped"

    url = f"{BASE_URL}/{filename}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            urllib.request.urlretrieve(
                url,
                output_path,
            )

            return "downloaded"

        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
        ) as error:

            if output_path.exists():
                output_path.unlink()

            if attempt == MAX_RETRIES:
                print(
                    f"FAILED {station_id}: {error}"
                )
                return "failed"

            print(
                f"Retrying {station_id} "
                f"(attempt {attempt + 1})"
            )

            time.sleep(RETRY_DELAY_SECONDS)


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates = load_candidates()

    downloaded = 0
    skipped = 0
    failed = 0

    total = len(candidates)

    print(f"Candidate stations: {total}")
    print()

    for index, station in enumerate(
        candidates,
        start=1,
    ):
        station_id = station["station_id"]

        print(
            f"[{index}/{total}] "
            f"{station['country_name']} "
            f"{station_id}"
        )

        result = download_station(station)

        if result == "downloaded":
            downloaded += 1

        elif result == "skipped":
            skipped += 1

        else:
            failed += 1

    print()
    print("Download complete")
    print("-----------------")
    print(f"Downloaded: {downloaded}")
    print(f"Already present: {skipped}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()