# Deterministic CI fixture

`python scripts/create_ci_fixture.py` replaces only the ignored `data/climatepulse_ci.duckdb`. It uses three synthetic stations: two in Germany and one in Austria. The source tables have the production schemas, fixed values, and a fixed provenance timestamp. The generator does not access NOAA or the network. It validates source counts and source grain before committing its transaction.

The fixture covers valid paired days; a quality flag; a sentinel; a missing TMAX and TMIN; a complete month, an empty month, and January months with 21/31 and 22/31 paired days. January baseline coverage is 20 years for one station and 21 for another. Austria has no January 2021 contributor. February 2021 produces an equal-country anomaly of 5 °C, compared with a direct station average of 4 °C. Observations in 2026 verify that complete-period models exclude that year.

General contracts and dbt schema tests run on both databases. Exact counts for the frozen 640-station production snapshot are tagged `production_snapshot` and excluded from CI. `test_ci_fixture_scenarios` is enabled only for the CI target and checks the synthetic boundary cases. This keeps the 219 production tests active.

Run locally from the repository root:

```sh
python scripts/create_ci_fixture.py
dbt debug --profiles-dir . --target ci
dbt build --profiles-dir . --target ci --exclude tag:production_snapshot
dbt test --profiles-dir .
```

The CI database, WAL, dbt output, and raw NOAA files are ignored by Git. CI does not build or modify the production DuckDB file.
