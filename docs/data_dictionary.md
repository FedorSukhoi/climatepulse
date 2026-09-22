# Reporting data dictionary

All dashboard tables are exported unchanged from dbt `main_marts` tables. The full column-level contracts and dbt schema tests are in [`models/marts/_marts__models.yml`](../models/marts/_marts__models.yml). Each export preserves the modeled grain and nulls.

| Table | Grain | Key | Main measures |
|---|---|---|---|
| `dim_locations` | Final station | `station_id` | Country identifiers, name, coordinates, frozen selection completeness |
| `fct_anomalies` | Station and recent month | `station_id`, `month_start` | Paired-day count, monthly completeness, baseline mean and coverage, eligibility, nullable anomaly in °C |
| `agg_country_monthly_anomalies` | Covered country and recent month | `iso_alpha2`, `month_start` | Eligible and total stations, contribution ratio, nullable country mean in °C |
| `agg_included_countries_monthly_anomalies` | Recent month | `month_start` | Included and represented countries, contributor counts and ratios, equal-country mean in °C |

`is_anomaly_eligible` is true only when the recent station-month meets the 70% paired-day rule and the same calendar-month baseline has at least 21 eligible years. Ineligible `temperature_anomaly_c` is null. A country-month mean is null when no station contributes. The monthly aggregate averages only available country means and exposes the number of included countries. `eu27_target_country_count` is 27 for context; it is not the number of represented countries.

All complete-period month keys are January 2021 through December 2025. Temperatures and anomalies are Celsius. No missing value is set to zero. See [mart contracts](mart_contracts.md) and [anomaly methodology](anomaly_methodology.md) for derivations.
