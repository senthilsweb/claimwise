# Building a Healthcare Revenue Cycle Management Data Pipeline with dbt

## Background
Healthcare Revenue Cycle Management (RCM) is a critical financial process that tracks patient care episodes from registration and appointment scheduling through the final payment of a balance. This project demonstrates how to build a modern data pipeline for RCM using dbt (data build tool), focusing on maintainability, scalability, and data quality.

## Use Case Scenario
The solution models the complete lifecycle of healthcare revenue:
- Patient encounters and medical services
- Claims processing and submissions
- Payment collections and reconciliation
- Provider and payer relationships
- Facility utilization and performance

## Project Structure
```plaintext
healthcare_analytics/
├── analyses/
├── macros/
│   └── helpers/
│       ├── generate_schema_name.sql
│       └── materialized_type.sql
├── models/
│   ├── raw/            # Source tables after seeding
│   ├── staging/        # Clean, typed source data
│   ├── intermediate/   # Business entity models
│   └── mart/          
│       ├── admin/      # Staff and operational analytics
│       ├── billing/    # Claims and revenue analytics
│       ├── clinical/   # Patient care analytics
│       └── core/       # Shared dimensions
├── seeds/
│   └── healthcare_data/
├── tests/
├── dbt_project.yml
└── packages.yml
```

## Libraries and Packages
```yaml
packages:
  - package: dbt-labs/dbt_external_tables
  - package: dbt-labs/codegen
  - package: calogica/dbt_date
  - package: dbt-labs/dbt_utils
  - package: elementary-data/elementary
```

## Data Architecture

### Source Layer (Raw)
Base tables seeded from CSV files:
- users (multi-type entity)
- facilities
- health_plans
- encounters
- claims
- activities
- collections

### Staging Layer
Generated using dbt codegen package:
- Standardized naming conventions
- Proper data types
- Basic data quality checks
- Case-sensitive column handling

### Intermediate Layer Transformations

#### Patient Entity (int_patients)
- Patient history aggregation
- Encounter metrics
- Claims history
- Healthcare utilization patterns

#### Doctor Entity (int_doctors)
- Patient load metrics
- Facility relationships
- Encounter statistics
- Performance indicators

#### Payer Entity (int_payers)
- Claims processing metrics
- Payment patterns
- Provider network details
- Plan performance data

#### Staff Entity (int_staff)
- Departmental organization
- Role-based segmentation
- Operational assignments

### Mart Layer

#### Core Dimensions
- dim_date: Time-based analysis support
- dim_facility: Location metrics
- dim_department: Organizational structure
- dim_health_plan: Insurance product details

#### Clinical Analytics
- dim_patient: Complete patient profile
- dim_doctor: Provider metrics
- dim_diagnosis: Clinical categorization
- fct_encounters: Visit records

#### Billing Analytics
- dim_payer: Insurance details
- fct_claims: Billing transactions
- fct_claim_activities: Processing events
- fct_collections: Payment tracking

#### Administrative Analytics
- dim_staff: Employee records
- Operational metrics

## Project Implementation Steps

### Initial Setup
```bash
dbt debug
dbt deps
```

### Data Loading
```bash
dbt seed
```

### Model Generation
```bash
# Generate source YAML
dbt run-operation generate_source --args '{
   "schema_name": "raw",
    "generate_columns": true,
    "include_descriptions": true,
    "include_data_types": true,
    "case_sensitive_cols" : true
}'

# Generate staging models
dbt run-operation generate_base_model --args '{"source_name": "raw", "table_name": "activities", "case_sensitive_cols": true}'
# [Repeat for other tables]
```

### Model Building
```bash
dbt run --select staging
dbt run --select intermediate
dbt run --select mart.core
dbt run --select mart.admin
dbt run --select mart.billing
dbt run --select mart.clinical
```

### Documentation
```bash
dbt docs generate
dbt docs serve
```
