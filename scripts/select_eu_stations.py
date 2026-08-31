from pathlib import Path
import csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EU_COUNTRIES_FILE = PROJECT_ROOT / "data/reference/eu27_countries.csv"
STATIONS_FILE = PROJECT_ROOT / "data/raw/metadata/ghcnd-stations.txt"
INVENTORY_FILE = PROJECT_ROOT / "data/raw/metadata/ghcnd-inventory.txt"

OUTPUT_FILE = PROJECT_ROOT / "data/processed/eu27_candidate_stations.csv"


BASELINE_START_YEAR = 1991
RECENT_START_YEAR = 2021


def load_eu_country_codes():
    """Return a dictionary keyed by NOAA country code."""

    countries = {}

    with EU_COUNTRIES_FILE.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            countries[row["noaa_country_code"]] = {
                "country_name": row["country_name"],
                "iso_alpha2": row["iso_alpha2"],
            }

    return countries


def load_stations(eu_countries):
    """Parse the NOAA fixed-width station metadata file."""

    stations = {}

    with STATIONS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            station_id = line[0:11].strip() # here and after: NOAA metadata fixed with processing
            country_code = station_id[:2]

            if country_code not in eu_countries:
                continue

            stations[station_id] = {
                "station_id": station_id,
                "noaa_country_code": country_code,
                "country_name": eu_countries[country_code]["country_name"],
                "iso_alpha2": eu_countries[country_code]["iso_alpha2"],
                "latitude": line[12:20].strip(),
                "longitude": line[21:30].strip(),
                "elevation_m": line[31:37].strip(),
                "station_name": line[41:71].strip(),
            }

    return stations


def load_temperature_inventory(stations):
    """Collect TMAX and TMIN coverage for EU candidate stations."""

    coverage = {}

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            station_id = line[0:11].strip()

            if station_id not in stations:
                continue

            element = line[31:35].strip()

            if element not in {"TMAX", "TMIN"}:
                continue

            first_year = int(line[36:40].strip())
            last_year = int(line[41:45].strip())

            if station_id not in coverage:
                coverage[station_id] = {}

            coverage[station_id][element] = {
                "first_year": first_year,
                "last_year": last_year,
            }

    return coverage


def find_candidates(stations, coverage):
    """Return stations meeting our initial period-of-record requirements."""

    candidates = []

    for station_id, station in stations.items():
        station_coverage = coverage.get(station_id, {})

        if "TMAX" not in station_coverage or "TMIN" not in station_coverage:
            continue

        tmax = station_coverage["TMAX"]
        tmin = station_coverage["TMIN"]

        historical_coverage = (
            tmax["first_year"] <= BASELINE_START_YEAR
            and tmin["first_year"] <= BASELINE_START_YEAR
        )

        recent_coverage = (
            tmax["last_year"] >= RECENT_START_YEAR
            and tmin["last_year"] >= RECENT_START_YEAR
        )

        if not historical_coverage or not recent_coverage:
            continue

        candidates.append(
            {
                **station,
                "tmax_first_year": tmax["first_year"],
                "tmax_last_year": tmax["last_year"],
                "tmin_first_year": tmin["first_year"],
                "tmin_last_year": tmin["last_year"],
            }
        )

    return candidates


def write_candidates(candidates):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "station_id",
        "noaa_country_code",
        "country_name",
        "iso_alpha2",
        "latitude",
        "longitude",
        "elevation_m",
        "station_name",
        "tmax_first_year",
        "tmax_last_year",
        "tmin_first_year",
        "tmin_last_year",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)


def main():
    eu_countries = load_eu_country_codes()

    print(f"EU countries loaded: {len(eu_countries)}")

    stations = load_stations(eu_countries)

    print(f"EU stations found in NOAA metadata: {len(stations)}")

    coverage = load_temperature_inventory(stations)

    candidates = find_candidates(stations, coverage)

    write_candidates(candidates)

    print(f"Candidate stations: {len(candidates)}")
    print(f"Output written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()