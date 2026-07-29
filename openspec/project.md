# Project Context

## Purpose
Healthcare Revenue Cycle Management (RCM) analytics pipeline: seeds raw claims/encounters/collections data, transforms it through a medallion architecture (bronze → silver → gold), and serves dimensional models (star schema) plus a metric layer for BI and dashboards.

## Tech Stack
- dbt-core 1.10.x
- DuckDB (dev, local file) / Databricks (prod, Unity Catalog + Delta)
- Elementary (data observability, prod only)
- Docker (prod runner image), Make (task runner)

## Conventions
- Medallion layers: `bronze` (seeds/sources) → `silver` (staging + intermediate, one schema) → `gold` (core / clinical / billing / admin / metrics)
- Column naming: source camelCase, **unquoted** identifiers only (resolved 2026-07-17 — quoted identifiers break on Databricks serverless SQL warehouses); surrogate keys renamed `*_id → *_key` via `process_column_name` macro
- All credentials via environment variables — never hardcoded
- Cross-warehouse SQL only: `dbt_utils` / `dbt_date` macros over dialect-specific functions
- Synthetic data volumes are not uniform random where realism matters — claim status and collection recovery are weighted (see `data-generator/README.md`)

## Structure
Claimwise monorepo — three apps plus repo-level specs:
- `dbt-pipeline/` — the dbt project (models/bronze|silver|gold, seeds, macros, tests, Dockerfile, Makefile)
- `data-generator/` — synthetic RCM data generator (Python CLI `rcm_module.py`, Marimo notebook, own Dockerfile)
- `slides/` — reveal.js presentation (medallion-aligned)
- `openspec/` — specs and change proposals

## Roadmap
- Add dbt exposures/reports to make this a full-fledged example dataset + apps
- Companion repo `claimwise-agents` (Strands + Bedrock AgentCore): one agent per bounded context over this gold layer
