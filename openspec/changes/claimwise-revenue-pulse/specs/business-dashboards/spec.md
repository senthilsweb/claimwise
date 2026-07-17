# Spec: business-dashboards

## ADDED Requirements

### Requirement: Dashboard is versioned code, deployed by command
The AI/BI dashboard SHALL be a serialized `.lvdash.json` file in `dashboards/`, deployed with `make dashboard TARGET=prod` (create-or-update by display name, then publish). No click-built state is the source of truth.

#### Scenario: Redeploy after edit
- **WHEN** the JSON is edited and `make dashboard TARGET=prod` runs
- **THEN** the existing dashboard updates in place at the same URL

### Requirement: Three business pages over the gold layer
The dashboard SHALL contain Executive Overview (KPI counters + trend + status mix + AR aging), Claims Operations (funnel, denial analysis, work-list table), and Payers & Providers (payer scorecard, AR by payer/bucket, department activity). Every dataset SHALL query `gold.mtr_*` only.

#### Scenario: Widget provenance
- **WHEN** any widget's dataset is inspected
- **THEN** its query reads from a `gold.mtr_*` model (or a UC metric view over gold)

### Requirement: Lineage reaches the dashboard
Unity Catalog SHALL show the dashboard as a downstream consumer of the gold tables it queries, and the dbt exposure SHALL declare the same dependency with the deployed URL.

#### Scenario: Tracing from source
- **WHEN** lineage is opened on bronze.claims and walked downstream
- **THEN** the path bronze.claims → silver.stg_claims → gold facts → gold.mtr_* → Claimwise Revenue Pulse is visible
