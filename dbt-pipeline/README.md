# Claimwise dbt Pipeline

Claimwise healthcare revenue cycle management (RCM) analytics built with dbt. Runs on
DuckDB for local development (no infrastructure) and Databricks (Unity
Catalog + Delta) in production. Snowflake support is planned as phase 2.

## Architecture

Medallion layers:

```
seeds (bronze) → silver (staging + intermediate) → gold
```

Gold models are grouped into four domains: `core`, `clinical`, `billing`,
and `admin`.

## Quick Start (dev, DuckDB)

No Docker required — dev runs against a local `rcm.duckdb` file.

```bash
python3 -m venv .venv && source .venv/bin/activate
make setup deps seed build
```

Copying `cp .env.example .env` is optional for dev; the defaults work as-is.

## Production (Databricks)

```bash
cp .env.example .env   # fill in DATABRICKS_HOST, DATABRICKS_HTTP_PATH,
                       # DATABRICKS_TOKEN, DATABRICKS_CATALOG
```

Then run either bare:

```bash
make daily TARGET=prod
```

or in Docker:

```bash
make docker-build && make docker-daily
```

## Observability (both disabled by default)

- **Elementary** — set `ENABLE_ELEMENTARY=true` in `.env`. Prod only (it does
  not support DuckDB); the report is written to `reports/elementary_report.html`.
- **OpenLineage** — set `ENABLE_OPENLINEAGE=true` and `OPENLINEAGE_URL` (e.g. a
  Marquez endpoint) in `.env`, and `pip install openlineage-dbt` (the Docker
  image already includes it). `seed`, `run`, `test`, and `build` then go through
  the `dbt-ol` wrapper and emit lineage events. Optional: `OPENLINEAGE_NAMESPACE`
  (default `claimwise`) and `OPENLINEAGE_API_KEY`.

## Make Targets

| Target | Description |
|---|---|
| `setup` | Install Python dependencies |
| `deps` | Install dbt packages |
| `seed` | Load bronze seed data |
| `build` | dbt build (run + test) |
| `test` | Run dbt tests |
| `daily` | Full daily pipeline (+ Elementary on prod when `ENABLE_ELEMENTARY=true`) |
| `report` | Generate Elementary report (prod only) |
| `docker-build` | Build the prod runner image |
| `docker-daily` | Run the daily pipeline in Docker |
| `clean` | Remove build artifacts and local DuckDB file |

All targets accept `TARGET=prod` (default `dev`).

## Project Layout

This is a monorepo: the dbt pipeline at the root, plus a synthetic data
generator and a presentation deck.

```
models/
  bronze/         # source definitions over seed data
  silver/         # 1:1 staging models over bronze sources
    intermediate/ # denormalized business logic (silver schema)
  gold/           # core | clinical | billing | admin
    metrics/      # mtr_* metric layer — every KPI computed once here
seeds/            # bronze CSV source data
macros/
tests/            # singular data-quality tests
data-generator/   # synthetic RCM data (Python CLI + Marimo notebook)
slides/           # reveal.js architecture deck
openspec/         # change proposals and specs
```

### Data Generator

```bash
pip install -r data-generator/requirements.txt
python data-generator/rcm_module.py --patients 100 --claims 300   # CSV to ./output
python data-generator/rcm_module.py --format duckdb               # or straight to DuckDB
```

See `data-generator/README.md` for options. Slides: open `slides/index.html`.

### Dashboard (Databricks AI/BI)

`make dashboard` deploys the Claimwise Revenue Pulse dashboard from
`dashboards/claimwise-revenue-pulse.lvdash.json` (see `dashboards/README.md`).
It reads only the `gold.mtr_*` metric layer; `make metricview` additionally
creates the Unity Catalog metric view `gold.claimwise_metrics`.

## Phase 2: Snowflake

Add `dbt-snowflake` and a new profile output — the SQL is already portable
(unquoted identifiers resolve case-insensitively on Snowflake too, and
`listagg` works unchanged).

## More

- `docs/` — RCM domain documentation (invoices, EOB statements, data model)
- `openspec/` — specs and change proposals
