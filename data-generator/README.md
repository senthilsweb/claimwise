# Claimwise Synthetic Data Generator

Generate realistic healthcare revenue cycle management (RCM) synthetic data for **Claimwise** — a fictitious healthcare company used to tell this demo's data story — for testing, demos, and development.

## Features

- **Configurable Volume**: Control the number of patients, providers, encounters, claims, and more
- **Realistic Data**: Uses Faker for realistic names, addresses, medical codes, and relationships
- **Multiple Formats**: Export to CSV, Parquet, JSON, or DuckDB
- **DuckDB Multi-Schema**: Simulates Claimwise's source systems with separate schemas (MSSQL, Oracle, S3)
- **Interactive UI**: Marimo notebook with sliders and controls
- **CLI Support**: Command-line interface for automation and CI/CD
- **Docker Ready**: Containerized for easy deployment

## Data Model

The generator creates 7 interrelated datasets that match the Claimwise dbt
pipeline seed schema (bronze layer) exactly — the output can be dropped into
`dbt-pipeline/seeds/healthcare_data/` and the full pipeline (including all
data-quality tests) builds green against it:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Users     │     │  Facilities │     │ Health Plans│
│ (Patients,  │     │             │     │  (by Payer) │
│  Doctors,   │     │             │     │             │
│Staff,Payers)│     │             │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └─────────┬─────────┘                   │
                 │                             │
                 ▼                             │
         ┌─────────────┐                       │
         │  Encounters │                       │
         │             │                       │
         └─────────────┘                       │
                                               │
         ┌─────────────┐◄──────────────────────┘
         │   Claims    │
         │             │
         └──────┬──────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│ Activities  │   │ Collections │
│             │   │ (Approved   │
│             │   │ claims only)│
└─────────────┘   └─────────────┘
```

### Dataset Descriptions

| Dataset | Description | Key Fields |
|---------|-------------|------------|
| **users** | Patients, doctors, staff, and payers | id, userID, userType, name, specialty, department, role |
| **facilities** | Healthcare facilities | id, facilityID, name, location, contactInfo |
| **health_plans** | Insurance plans by payer | id, healthPlanID, planName, payerID |
| **encounters** | Patient visits | id, encounterID, patientID, doctorID, facilityID, date |
| **claims** | Medical claims | id, claimID, patientID, payerID, status, amount |
| **activities** | Claim lifecycle events | id, activityID, claimID, activityDate, activityType |
| **collections** | Payment collections | id, collectionID, claimID, methodOfCollection, amountCollected |

Business identifiers carry domain prefixes (CLM, COL, ENC, ACT, FAC, HP, and
DR/PT/STF/PAY per user type), matching the pipeline's format-validation tests.

## Quick Start

### Prerequisites

- Python 3.10+
- pip or conda

### Installation

```bash
# Clone this repository
git clone https://github.com/senthilsweb/claimwise.git
cd claimwise/data-generator

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
| `--payers` | 10 | Number of insurance payers |
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

Generate data directly into DuckDB with schemas that simulate Claimwise's source systems:

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
| `claims_proc` | Oracle Claims Processing | claims, activities, collections, health_plans |
| `s3_landing` | S3 Raw Landing Zone | All 7 tables (raw CSV equivalent) |

**Querying the DuckDB database:**

```sql
-- Connect to the database
duckdb ./output/rcm.duckdb

-- View schema summary
SELECT * FROM main.schema_summary;

-- Query patient management system (MSSQL)
SELECT * FROM patient_mgmt.users WHERE "userType" = 'PATIENT' LIMIT 10;

-- Query claims processing system (Oracle)
SELECT * FROM claims_proc.claims WHERE status = 'Approved';

-- Query raw landing zone (S3)
SELECT * FROM s3_landing.encounters;

-- Join across schemas (simulating cross-system analytics)
SELECT
    p.name,
    c."claimID",
    c.amount,
    c.status
FROM patient_mgmt.users p
JOIN claims_proc.claims c ON p.id = c."patientID"
WHERE p."userType" = 'PATIENT';
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
├── users.csv           # All users (patients, doctors, staff, payers)
├── facilities.csv      # Healthcare facilities
├── health_plans.csv    # Insurance plans
├── encounters.csv      # Patient encounters
├── claims.csv          # Medical claims
├── activities.csv      # Claim lifecycle events
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
    │   ├── activities
    │   ├── collections
    │   └── health_plans
    └── s3_landing/            # S3 - Raw Landing Zone
        ├── users
        ├── facilities
        ├── health_plans
        ├── encounters
        ├── claims
        ├── activities
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
- **Prefixed Medical Codes**: ICD- diagnosis codes and CPT- procedure codes
- **Logical Relationships**: Claims reference patients and payers; activities and collections reference claims
- **Business Rules Enforced**: Collections only against approved claims and never exceeding the claim amount; every claim has at least one activity
- **Proper Date Sequences**: Claim activities fall inside the claim's created/updated window; no future dates

The output passes the dbt pipeline's full test suite (uniqueness, not-null,
accepted values, ID formats, referential integrity, reconciliation).

## License

MIT License - Free for commercial and personal use.
