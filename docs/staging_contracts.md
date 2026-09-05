| File                                         | Reads                                                                        | Produces or verifies                                                                                                                                                                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/ingest_project_inputs_to_duckdb.py` | Three project CSVs                                                           | Creates `raw.final_stations`, `raw.eu27_countries`, and `raw.analysis_parameters` transactionally. Verifies 640 stations, 15 represented countries, 27 EU countries, six expected parameters, and valid country-code relationships. |
| `models/sources/_climatepulse__sources.yml`  | Three raw project-input tables                                               | Registers them as dbt sources. Adds not-null, uniqueness, accepted-value, and relationship tests.                                                                                                                                   |
| `stg_noaa__observations.sql`                 | `raw.noaa_daily_observations` through `source('noaa', 'daily_observations')` | Creates `main_staging.stg_noaa__observations`. Removes quality-flagged and sentinel records, converts tenths of degrees to Celsius, and retains all 971 candidate stations.                                                         |
| `stg_noaa__stations.sql`                     | `raw.final_stations`                                                         | Creates `main_staging.stg_noaa__stations`, the clean interface to the frozen 640-station universe.                                                                                                                                  |
| `stg_reference__countries.sql`               | `raw.eu27_countries`                                                         | Creates the complete 27-country NOAA-to-ISO reference view.                                                                                                                                                                         |
| `stg_reference__analysis_parameters.sql`     | `raw.analysis_parameters`                                                    | Creates a renamed, long-form parameter view. Values remain strings pending typed transformation in Checkpoint 9.                                                                                                                    |
| `_noaa__models.yml`                          | The two NOAA staging views                                                   | Documents their columns and tests required fields, station uniqueness, accepted temperature elements, and country relationships.                                                                                                    |
| `_reference__models.yml`                     | The two reference staging views                                              | Documents and tests unique country codes, parameter names, required values, and allowed parameter names.                                                                                                                            |




| Test                                 | Table checked             | Failure condition                                                          |
| ------------------------------------ | ------------------------- | -------------------------------------------------------------------------- |
| `test_analysis_parameter_values.sql` | `raw.analysis_parameters` | Any of the six frozen parameter values is missing, changed, or unexpected. |
| `test_eu27_country_universe.sql`     | `raw.eu27_countries`      | The table does not contain exactly 27 unique NOAA and ISO codes.           |
| `test_final_station_thresholds.sql`  | `raw.final_stations`      | A station violates the 80% overall or 70% monthly completeness rule.       |
| `test_final_station_universe.sql`    | `raw.final_stations`      | The frozen universe is not exactly 640 stations across 15 countries.       |




| Test                                               | Tables checked                       | Failure condition                                                                                                                                  |
| -------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_stg_noaa__observations_unique_grain.sql`     | `stg_noaa__observations`             | More than one row exists for a station, date, and temperature element.                                                                             |
| `test_stg_noaa__observations_reconcile_source.sql` | Raw and staged observations          | Filtered row count or temperature count/sum/range differs from the raw-source calculation. This also verifies the Celsius conversion collectively. |
| `test_stg_noaa__station_universe.sql`              | `stg_noaa__stations`                 | The staged universe differs from 640 stations and 15 countries.                                                                                    |
| `test_stg_noaa__station_ranges.sql`                | `stg_noaa__stations`                 | Coordinates or completeness values fall outside their valid ranges.                                                                                |
| `test_stg_noaa__station_country_mapping.sql`       | Staged stations and countries        | A station’s NOAA code, ISO code, and country name do not resolve as one consistent mapping.                                                        |
| `test_stg_reference__country_universe.sql`         | `stg_reference__countries`           | The staged reference is not the complete EU-27 universe.                                                                                           |
| `test_stg_reference__parameter_values.sql`         | `stg_reference__analysis_parameters` | Staging altered or omitted a frozen methodology value.                                                                                             |



