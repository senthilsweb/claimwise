# RCM Synthetic Data Generator

Generate realistic healthcare revenue cycle management (RCM) synthetic data for testing, demos, and development.

## Features

- **Configurable Volume**: Control the number of patients, providers, encounters, claims, and more
- **Realistic Data**: Uses Faker for realistic names, addresses, medical codes, and relationships
- **Multiple Formats**: Export to CSV, Parquet, JSON, or DuckDB
- **DuckDB Multi-Schema**: Simulates source systems with separate schemas (MSSQL, Oracle, S3)
- **Interactive UI**: Marimo notebook with sliders and controls
- **CLI Support**: Command-line interface for automation and CI/CD
- **Docker Ready**: Containerized for easy deployment

## Data Model

The generator creates 7 interrelated datasets following the healthcare RCM domain:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Users     │     │  Facilities │     │ Health Plans│
│ (Patients,  │     │             │     │             │
│  Doctors,   │     │             │     │             │
│  Staff)     │     │             │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └─────────┬─────────┘                   │
                 │                             │
                 ▼                             │
         ┌─────────────┐                       │
         │  Encounters │                       │
         │             │                       │
         └──────┬──────┘                       │
                │                              │
                ▼                              │
         ┌─────────────┐◄──────────────────────┘
         │   Claims    │
         │             │
         └──────┬──────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│   Claim     │   │ Collections │
│ Activities  │   │             │
└─────────────┘   └─────────────┘
```

### Dataset Descriptions

| Dataset | Description | Key Fields |
|---------|-------------|------------|
| **users** | Doctors, staff, and patients | user_id, role, name, specialty, npi |
| **facilities** | Healthcare facilities | facility_id, name, type, address, npi |
| **health_plans** | Insurance plans | plan_id, payer_name, plan_type, deductible |
| **encounters** | Patient visits | encounter_id, patient_id, provider_id, diagnosis_code |
| **claims** | Medical claims | claim_id, encounter_id, billed_amount, status |
| **claim_activities** | Claim lifecycle events | activity_id, claim_id, action, action_date |
| **collections** | Payment collections | collection_id, claim_id, amount_collected |

## Quick Start

### Prerequisites

- Python 3.10+
- pip or conda

### Installation

```bash
# Clone or download this repository
cd rcm-data-generator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Option 1: Marimo Notebook (Interactive)

```bash
# Run the interactive notebook
marimo run rcm_generator.py

# Or edit the notebook
marimo edit rcm_generator.py
```

The notebook provides interactive sliders and controls:
- **Patient/Provider counts**: Adjust the number of each user type
- **Encounter/Claim volumes**: Control transaction volumes
- **Date range**: Set the time period for generated data
- **Output format**: Choose between CSV, Parquet, or JSON

#### Option 2: Command Line

```bash
# Basic usage with defaults
python rcm_module.py

# Customize volumes
python rcm_module.py \
  --patients 500 \
  --doctors 50 \
  --encounters 1000 \
  --claims 1500 \
  --format parquet \
  --output-dir ./data

# Full options
python rcm_module.py \
  --patients 200 \
  --doctors 30 \
  --staff 25 \
  --facilities 15 \
  --encounters 500 \
  --claims 800 \
  --activities-per-claim 4 \
  --start-date 2023-01-01 \
  --end-date 2024-01-01 \
  --format csv \
  --output-dir ./output \
  --seed 42
```

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--patients` | 100 | Number of patients to generate |
| `--doctors` | 20 | Number of doctors to generate |
| `--staff` | 15 | Number of staff members |
| `--facilities` | 10 | Number of healthcare facilities |
| `--encounters` | 200 | Number of patient encounters |
| `--claims` | 300 | Number of medical claims |
| `--activities-per-claim` | 3 | Average activities per claim |
| `--start-date` | 1 year ago | Start date (YYYY-MM-DD) |
| `--end-date` | today | End date (YYYY-MM-DD) |
| `--format` | csv | Output format (csv, parquet, json, **duckdb**) |
| `--output-dir` | ./output | Output directory for csv/parquet/json |
| `--duckdb-path` | ./output/rcm.duckdb | DuckDB database file path |
| `--seed` | None | Random seed for reproducibility |

### DuckDB Multi-Schema Output

Generate data directly into DuckDB with schemas that simulate the source systems:

```bash
# Generate DuckDB database with multi-schema layout
python rcm_module.py --format duckdb --patients 500 --claims 1500

# Custom database path
python rcm_module.py --format duckdb --duckdb-path ./data/demo.duckdb
```

**Schema Layout:**

| Schema | Source System | Tables |
|--------|---------------|--------|
| `patient_mgmt` | MSSQL Patient Management | users, facilities, encounters |
| `claims_proc` | Oracle Claims Processing | claims, claim_activities, collections, health_plans |
| `s3_landing` | S3 Raw Landing Zone | All 7 tables (raw CSV equivalent) |

**Querying the DuckDB database:**

```sql
-- Connect to the database
duckdb ./output/rcm.duckdb

-- View schema summary
SELECT * FROM main.schema_summary;

-- Query patient management system (MSSQL)
SELECT * FROM patient_mgmt.users WHERE role = 'Patient' LIMIT 10;

-- Query claims processing system (Oracle)
SELECT * FROM claims_proc.claims WHERE status = 'Approved';

-- Query raw landing zone (S3)
SELECT * FROM s3_landing.encounters;

-- Join across schemas (simulating cross-system analytics)
SELECT
    p.patient_name,
    c.claim_id,
    c.billed_amount,
    c.status
FROM patient_mgmt.users p
JOIN claims_proc.claims c ON p.user_id = c.patient_id
WHERE p.role = 'Patient';
```

## Docker Usage

### Build and Run

```bash
# Build the image
docker build -t rcm-generator .

# Run with default settings
docker run -v $(pwd)/output:/app/output rcm-generator

# Run with custom settings
docker run -v $(pwd)/output:/app/output rcm-generator \
  python rcm_module.py \
  --patients 500 \
  --claims 1000 \
  --format parquet
```

### Docker Compose

```bash
# Generate data
docker-compose up generate

# Run Marimo notebook (accessible at http://localhost:8080)
docker-compose up notebook
```

## Output Structure

### CSV/Parquet/JSON Output
```
output/
├── users.csv           # All users (patients, doctors, staff)
├── facilities.csv      # Healthcare facilities
├── health_plans.csv    # Insurance plans
├── encounters.csv      # Patient encounters
├── claims.csv          # Medical claims
├── claim_activities.csv # Claim lifecycle events
└── collections.csv     # Payment collections
```

### DuckDB Output
```
output/
└── rcm.duckdb
    ├── patient_mgmt/          # MSSQL - Patient Management System
    │   ├── users
    │   ├── facilities
    │   └── encounters
    ├── claims_proc/           # Oracle - Claims Processing System
    │   ├── claims
    │   ├── claim_activities
    │   ├── collections
    │   └── health_plans
    └── s3_landing/            # S3 - Raw Landing Zone
        ├── users
        ├── facilities
        ├── health_plans
        ├── encounters
        ├── claims
        ├── claim_activities
        └── collections
```

## Sample Data Volumes

| Profile | Patients | Doctors | Encounters | Claims | Est. Records |
|---------|----------|---------|------------|--------|--------------|
| **Demo** | 50 | 10 | 100 | 150 | ~1,500 |
| **Small** | 100 | 20 | 200 | 300 | ~3,000 |
| **Medium** | 500 | 50 | 1,000 | 1,500 | ~15,000 |
| **Large** | 2,000 | 100 | 5,000 | 7,500 | ~75,000 |

## Use Cases

1. **Development & Testing**: Generate test data for healthcare applications
2. **Demo Environments**: Create realistic demo data for presentations
3. **Data Pipeline Testing**: Test ETL pipelines with realistic healthcare data
4. **Analytics Prototyping**: Build analytics dashboards with sample data
5. **Training & Education**: Learn healthcare RCM data modeling

## Data Quality

The generated data includes:

- **Realistic Names & Addresses**: Using Faker library
- **Valid Medical Codes**: ICD-10 diagnosis codes, CPT procedure codes
- **Proper NPI Numbers**: 10-digit provider identifiers
- **Logical Relationships**: Encounters link to claims, claims to activities
- **Realistic Amounts**: Billed, allowed, and paid amounts follow industry patterns
- **Proper Date Sequences**: Encounters → Claims → Activities → Collections

## License

MIT License - Free for commercial and personal use.
