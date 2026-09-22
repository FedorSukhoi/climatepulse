"""Export tested dbt marts as a small, versioned Evidence CSV contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
MARTS = {
    'dim_locations': (640, 'station_id'),
    'fct_anomalies': (38400, 'station_id, month_start'),
    'agg_country_monthly_anomalies': (900, 'iso_alpha2, month_start'),
    'agg_included_countries_monthly_anomalies': (60, 'month_start'),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', type=Path, default=ROOT / 'data/climatepulse.duckdb')
    parser.add_argument('--output', type=Path, default=ROOT / 'dashboard/sources/climatepulse')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'source': 'ClimatePulse production dbt marts', 'baseline': '1991-2020', 'recent': '2021-2025', 'tables': {}}
    with duckdb.connect(str(args.database.resolve()), read_only=True) as con:
        for name, (expected, order) in MARTS.items():
            table = f'main_marts.{name}'
            count = con.execute(f'select count(*) from {table}').fetchone()[0]
            if count != expected:
                raise ValueError(f'{name}: expected {expected} rows, found {count}')
            if name != 'dim_locations':
                invalid = con.execute(f"select count(*) from {table} where month_start < date '2021-01-01' or month_start >= date '2026-01-01'").fetchone()[0]
                if invalid:
                    raise ValueError(f'{name}: {invalid} rows outside complete period')
            path = output / f'{name}.csv'
            con.execute(f"copy (select * from {table} order by {order}) to ? (header true, delimiter ',')", [str(path)])
            manifest['tables'][name] = {'rows': count, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT / 'dashboard/data/export_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Exported {len(MARTS)} mart CSVs to {output}')


if __name__ == '__main__':
    main()
