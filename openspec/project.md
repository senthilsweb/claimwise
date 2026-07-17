# Project Context

## Purpose
Healthcare Revenue Cycle Management (RCM) analytics pipeline: seeds raw claims/encounters/collections data, transforms it through staging → intermediate → mart layers, and serves dimensional models (star schema) for BI.

## Tech Stack
- dbt-core 1.10.x
- DuckDB (dev, local file) / Databricks (prod, Unity Catalog + Delta)
- Elementary (data observability, prod only)
- Docker (prod runner image), Make (task runner)

## Conventions
- Layers: `staging` (views) → `intermediate` (views) → `mart` (tables), schemas `raw / staging / intermediate / mart`
- Column naming: source camelCase quoted (`"planName"`); surrogate keys renamed `*_id → *_key` via `process_column_name` macro
- All credentials via environment variables — never hardcoded
- Cross-warehouse SQL only: `dbt_utils` / `dbt_date` macros over dialect-specific functions

## Structure
Claimwise monorepo — three apps plus repo-level specs:
- `dbt-pipeline/` — the dbt project (models/staging|intermediate|mart, seeds, macros, tests, Dockerfile, Makefile)
- `data-generator/` — synthetic RCM data generator (Python CLI `rcm_module.py`, Marimo notebook, own Dockerfile)
- `slides/` — reveal.js presentation (to be standardized with the slide-deck skill)
- `openspec/` — specs and change proposals

## Roadmap
- Standardize `slides/index.html` with the slide-deck skill (~90% match today)
- Add dbt exposures/reports to make this a full-fledged example dataset + apps
