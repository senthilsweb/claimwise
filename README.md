# Claimwise

**Claimwise** is a fictitious healthcare company at the center of this Healthcare Revenue Cycle Management (RCM) analytics demo — a synthetic data generator and data lakehouse reference architecture inspired by dbt's [`jaffle_shop`](https://github.com/dbt-labs/jaffle-shop).

Just as `jaffle_shop` uses a fictitious e-commerce store to teach analytics engineering concepts, **Claimwise** uses a fictitious healthcare provider to tell an end-to-end data story — from patient encounters and medical claims born in source systems, through an S3 landing zone, into a modern lakehouse (staging → intermediate → marts), and out to dashboards and business reports like EOB statements.

This repository includes:

- **dbt Pipeline** - staging → intermediate → mart transformations on DuckDB (dev) and Databricks (prod)
- **Synthetic Data Generator** - Generate realistic Claimwise RCM data for testing and demos
- **Slide Deck** - Reveal.js presentation telling the Claimwise data story and explaining the data lakehouse architecture

## The Claimwise Story

Claimwise is a healthcare organization embracing data transformation. Its data is born in two source systems that land in a shared S3 zone and are transformed by a lakehouse pipeline:

| Source System | Technology | Feeds |
|----------------|------------|-------|
| Patient Management | MSSQL | users, facilities, encounters |
| Claims Processing | Oracle | claims, claim_activities, collections, health_plans |

`Landing Zone → Raw → Staging → Intermediate → Marts (Admin / Billing / Clinical) → Dashboards`

This Claimwise narrative carries through the whole demo: the data model, business glossary, data quality checks, lineage graph, and a sample multi-page EOB (Explanation of Benefits) statement are all told from Claimwise's point of view.

## Project Structure

```
claimwise/
├── dbt-pipeline/            # dbt project: DuckDB (dev) / Databricks (prod)
│   ├── models/              # staging → intermediate → mart
│   ├── seeds/               # raw CSV source data
│   ├── Makefile             # setup / build / test / daily
│   └── README.md            # Quick start
├── data-generator/          # Synthetic Claimwise RCM data generator
│   ├── rcm_generator.py     # Marimo interactive notebook
│   ├── rcm_module.py        # Python CLI module
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md            # Detailed documentation
├── slides/
│   └── index.html           # Reveal.js presentation (15 slides)
└── openspec/                # Specs and change proposals
```

### dbt Pipeline

```bash
cd dbt-pipeline
python3 -m venv .venv && source .venv/bin/activate
make setup deps seed build   # full build + tests on local DuckDB
```

See `dbt-pipeline/README.md` for the Databricks production setup.

## Quick Start

### Data Generator

```bash
cd data-generator

# Install dependencies
pip install -r requirements.txt

# Generate data (CSV) — the volume checked into dbt-pipeline/seeds/healthcare_data
python rcm_module.py --patients 1500 --claims 5000 --encounters 8000 \
  --start-date 2024-08-01 --end-date 2026-07-29 --seed 42

# Generate data (DuckDB with multi-schema)
python rcm_module.py --format duckdb --patients 500 --claims 1500

# Interactive notebook
marimo run rcm_generator.py
```

### Slide Deck

```bash
cd slides

# Open in browser
open index.html

# Or serve locally
python -m http.server 8000
# Then visit http://localhost:8000
```

## Data Generator Features

- **Configurable volumes**: Patients, doctors, facilities, encounters, claims
- **Multiple output formats**: CSV, Parquet, JSON, DuckDB
- **DuckDB multi-schema**: Simulates source systems (MSSQL, Oracle, S3)
- **Interactive UI**: Marimo notebook with sliders
- **Docker support**: Containerized execution

### Generated Datasets

| Dataset | Description |
|---------|-------------|
| users | Patients, doctors, and staff |
| facilities | Healthcare facilities |
| health_plans | Insurance plans |
| encounters | Patient visits |
| claims | Medical claims |
| claim_activities | Claim lifecycle events |
| collections | Payment collections |

### DuckDB Schema Layout

| Schema | Simulates | Tables |
|--------|-----------|--------|
| `patient_mgmt` | MSSQL | users, facilities, encounters |
| `claims_proc` | Oracle | claims, claim_activities, collections, health_plans |
| `s3_landing` | S3 Raw | All 7 tables |

## Slide Deck Topics

1. Title & Introduction
2. Agenda
3. Use Case - The Claimwise Data Story
4. RCM Demo Datasets
5. Staging Layer - Data Models
6. Intermediate Layer - Persona Views
7. Marts Layer - Star Schema
8. Business Glossary
9. Data Quality Checks
10. Data Lineage & Observability
11. Pipeline Scheduler Requirements
12. Business Reports - EOB Statement
13. Synthetic Data Generator
14. Generated Data Model
15. Summary & Key Takeaways

## Technology Stack

- **Data Generation**: Python, Faker, Pandas, DuckDB
- **Interactive UI**: Marimo
- **Presentation**: Reveal.js, Iconify icons
- **Containerization**: Docker

## License

MIT License - Free for commercial and personal use.
