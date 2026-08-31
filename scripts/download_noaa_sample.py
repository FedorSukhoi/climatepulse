from pathlib import Path
import csv
import urllib.request


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data/processed/eu27_candidate_stations.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data/raw/ghcn_daily/sample"
)

BASE_URL = (
    "https://www.ncei.noaa.gov/"
    "pub/data/ghcn/daily/by_station"
)


SAMPLE_COUNTRIES = {
    "DE": "Germany",
    "ES": "Spain",
    "FI": "Finland",
}


def select_sample_stations():
    """
    Select one candidate station from each sample country.
    """

    selected = {}

    with CANDIDATE_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            iso_code = row["iso_alpha2"]

            if (
                iso_code in SAMPLE_COUNTRIES
                and iso_code not in selected
            ):
                selected[iso_code] = row

    return selected


def download_station(station):
    """
    Download one compressed NOAA by-station CSV.
    """

    station_id = station["station_id"]

    filename = f"{station_id}.csv.gz"

    url = f"{BASE_URL}/{filename}"
    output_path = OUTPUT_DIR / filename

    print(
        f"Downloading {station['country_name']}: "
        f"{station['station_name']} ({station_id})"
    )

    urllib.request.urlretrieve(url, output_path)

    print(f"Saved to {output_path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stations = select_sample_stations()

    if len(stations) != len(SAMPLE_COUNTRIES):
        missing = set(SAMPLE_COUNTRIES) - set(stations)

        raise RuntimeError(
            f"No candidate station found for: {sorted(missing)}"
        )

    for station in stations.values():
        download_station(station)

    print()
    print(f"Downloaded {len(stations)} sample stations.")


if __name__ == "__main__":
    main()