# Claimwise dbt Pipeline

Claimwise healthcare revenue cycle management (RCM) analytics built with dbt. Runs on
DuckDB for local development (no infrastructure) and Databricks (Unity
Catalog + Delta) in production. Snowflake support is planned as phase 2.

## Architecture

```
seeds (raw) → staging → intermediate → mart
```

Mart models are grouped into four domains: `core`, `clinical`, `billing`,
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

The Elementary observability report is written to
`reports/elementary_report.html`. Elementary runs on prod only (it does not
support DuckDB).

## Make Targets

| Target | Description |
|---|---|
| `setup` | Install Python dependencies |
| `deps` | Install dbt packages |
| `seed` | Load raw seed data |
| `build` | dbt build (run + test) |
| `test` | Run dbt tests |
| `daily` | Full daily pipeline (seed, build, report on prod) |
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
  staging/        # 1:1 views over raw sources
  intermediate/   # denormalized business logic
  mart/           # core | clinical | billing | admin
seeds/            # raw CSV source data
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

## Phase 2: Snowflake

Add `dbt-snowflake` and a new profile output — the SQL is already portable
(quoted identifiers and `listagg` work unchanged on Snowflake).

## More

- `docs/` — RCM domain documentation (invoices, EOB statements, data model)
- `openspec/` — specs and change proposals
