# Evidence dashboard data contract

`dashboard/` is the Evidence project. Its `climatepulse` CSV source contains four checked-in exports from tested production dbt marts, not the raw or intermediate DuckDB database. The 3.6 MB contract lets a fresh checkout build the dashboard without the 372 MB production database. `scripts/export_marts_for_dashboard.py` checks each expected mart row count and the recent date range, writes deterministic ordered CSVs, and records each file's SHA-256 in `dashboard/data/export_manifest.json`.

Refresh after a full production `dbt build --profiles-dir .`:

```sh
.venv/bin/python scripts/export_marts_for_dashboard.py
cd dashboard
npm ci
npm run sources
npm run build
```

Review the changed manifest and mart CSV diff before committing an updated snapshot. A fresh NOAA download can alter historical observations; compare source checksums first. The dashboard does not recalculate baselines or country-first weighting. Its SQL selects or summarizes mart columns for presentation. Null country and station anomalies stay null; no 2026 data is exported. The dashboard should always show station or country counts beside a result.

The Evidence runtime is pinned in `package.json` and its dependency tree in `package-lock.json`. Local preview: `npm run dev` in `dashboard/`. The static output is `dashboard/build/` and is ignored by Git. Deploy that output through a static host only after a successful build and review of the snapshot manifest.
