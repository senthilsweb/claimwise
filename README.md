# RCM Analytics Demo

A complete Healthcare Revenue Cycle Management (RCM) analytics demo featuring:

- **Synthetic Data Generator** - Generate realistic RCM data for testing and demos
- **Slide Deck** - Reveal.js presentation explaining the data lakehouse architecture

## Project Structure

```
rcm-analytics-demo/
├── data-generator/          # Synthetic RCM data generator
│   ├── rcm_generator.py     # Marimo interactive notebook
│   ├── rcm_module.py        # Python CLI module
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md            # Detailed documentation
└── slides/
    └── index.html           # Reveal.js presentation (15 slides)
```

## Quick Start

### Data Generator

```bash
cd data-generator

# Install dependencies
pip install -r requirements.txt

# Generate data (CSV)
python rcm_module.py --patients 100 --claims 300

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
3. Use Case - The Data Story
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
