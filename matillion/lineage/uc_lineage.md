# Unity Catalog lineage for `claimwise`

Recorded automatically by Unity Catalog from the Matillion runs; read through the Databricks lineage API on 2026-11-08.
37 tables, 59 edges. In Databricks, open any table in Catalog Explorer and choose the Lineage tab for the interactive graph.

```mermaid
flowchart LR
  subgraph landing[landing volume]
    Volumes_claimwise_landing_raw_activities["activities.csv"]
    Volumes_claimwise_landing_raw_claims["claims.csv"]
    Volumes_claimwise_landing_raw_collections["collections.csv"]
    Volumes_claimwise_landing_raw_encounters["encounters.csv"]
    Volumes_claimwise_landing_raw_facilities["facilities.csv"]
    Volumes_claimwise_landing_raw_health_plans["health_plans.csv"]
    Volumes_claimwise_landing_raw_users["users.csv"]
  end
  subgraph bronze
    bronze_activities[activities]
    bronze_claims[claims]
    bronze_collections[collections]
    bronze_encounters[encounters]
    bronze_facilities[facilities]
    bronze_health_plans[health_plans]
    bronze_users[users]
  end
  subgraph silver
    silver_int_doctors[int_doctors]
    silver_int_patients[int_patients]
    silver_int_payers[int_payers]
    silver_int_staff[int_staff]
    silver_stg_activities[stg_activities]
    silver_stg_claims[stg_claims]
    silver_stg_collections[stg_collections]
    silver_stg_encounters[stg_encounters]
    silver_stg_facilities[stg_facilities]
    silver_stg_health_plans[stg_health_plans]
    silver_stg_users[stg_users]
  end
  subgraph gold
    gold_dim_date[dim_date]
    gold_dim_department[dim_department]
    gold_dim_diagnosis[dim_diagnosis]
    gold_dim_doctor[dim_doctor]
    gold_dim_facility[dim_facility]
    gold_dim_health_plan[dim_health_plan]
    gold_dim_patient[dim_patient]
    gold_dim_payer[dim_payer]
    gold_dim_staff[dim_staff]
    gold_fct_claim_activities[fct_claim_activities]
    gold_fct_claims[fct_claims]
    gold_fct_collections[fct_collections]
    gold_fct_encounters[fct_encounters]
    gold_mtr_ar_aging[mtr_ar_aging]
    gold_mtr_claims_funnel[mtr_claims_funnel]
    gold_mtr_department_activity[mtr_department_activity]
    gold_mtr_executive_summary[mtr_executive_summary]
    gold_mtr_payer_scorecard[mtr_payer_scorecard]
    gold_mtr_revenue_monthly[mtr_revenue_monthly]
  end
  Volumes_claimwise_landing_raw_activities --> bronze_activities
  Volumes_claimwise_landing_raw_claims --> bronze_claims
  Volumes_claimwise_landing_raw_collections --> bronze_collections
  Volumes_claimwise_landing_raw_encounters --> bronze_encounters
  Volumes_claimwise_landing_raw_facilities --> bronze_facilities
  Volumes_claimwise_landing_raw_health_plans --> bronze_health_plans
  Volumes_claimwise_landing_raw_users --> bronze_users
  bronze_activities --> silver_stg_activities
  bronze_claims --> silver_stg_claims
  bronze_collections --> silver_stg_collections
  bronze_encounters --> silver_stg_encounters
  bronze_facilities --> silver_stg_facilities
  bronze_health_plans --> silver_stg_health_plans
  bronze_users --> silver_stg_users
  gold_dim_payer --> gold_mtr_ar_aging
  gold_dim_payer --> gold_mtr_payer_scorecard
  gold_fct_claims --> gold_mtr_ar_aging
  gold_fct_claims --> gold_mtr_claims_funnel
  gold_fct_claims --> gold_mtr_executive_summary
  gold_fct_claims --> gold_mtr_payer_scorecard
  gold_fct_claims --> gold_mtr_revenue_monthly
  gold_fct_collections --> gold_mtr_ar_aging
  gold_fct_collections --> gold_mtr_executive_summary
  gold_fct_collections --> gold_mtr_payer_scorecard
  gold_fct_collections --> gold_mtr_revenue_monthly
  gold_fct_encounters --> gold_mtr_department_activity
  gold_fct_encounters --> gold_mtr_executive_summary
  silver_int_doctors --> gold_dim_doctor
  silver_int_doctors --> gold_fct_encounters
  silver_int_doctors --> gold_mtr_department_activity
  silver_int_patients --> gold_dim_patient
  silver_int_patients --> gold_fct_claims
  silver_int_patients --> gold_fct_encounters
  silver_int_payers --> gold_dim_payer
  silver_int_payers --> gold_fct_claims
  silver_int_staff --> gold_dim_staff
  silver_stg_activities --> gold_dim_diagnosis
  silver_stg_activities --> gold_fct_claim_activities
  silver_stg_claims --> gold_dim_health_plan
  silver_stg_claims --> gold_fct_claim_activities
  silver_stg_claims --> gold_fct_claims
  silver_stg_claims --> gold_fct_collections
  silver_stg_claims --> gold_mtr_executive_summary
  silver_stg_claims --> silver_int_patients
  silver_stg_claims --> silver_int_payers
  silver_stg_collections --> gold_fct_collections
  silver_stg_encounters --> gold_dim_facility
  silver_stg_encounters --> gold_fct_encounters
  silver_stg_encounters --> silver_int_doctors
  silver_stg_encounters --> silver_int_patients
  silver_stg_facilities --> gold_dim_facility
  silver_stg_facilities --> silver_int_doctors
  silver_stg_health_plans --> gold_dim_health_plan
  silver_stg_health_plans --> silver_int_payers
  silver_stg_users --> gold_dim_department
  silver_stg_users --> silver_int_doctors
  silver_stg_users --> silver_int_patients
  silver_stg_users --> silver_int_payers
  silver_stg_users --> silver_int_staff
```

| upstream | downstream |
|---|---|
| `/Volumes/claimwise/landing/raw/activities/` | `bronze.activities` |
| `/Volumes/claimwise/landing/raw/claims/` | `bronze.claims` |
| `/Volumes/claimwise/landing/raw/collections/` | `bronze.collections` |
| `/Volumes/claimwise/landing/raw/encounters/` | `bronze.encounters` |
| `/Volumes/claimwise/landing/raw/facilities/` | `bronze.facilities` |
| `/Volumes/claimwise/landing/raw/health_plans/` | `bronze.health_plans` |
| `/Volumes/claimwise/landing/raw/users/` | `bronze.users` |
| `silver.stg_users` | `gold.dim_department` |
| `silver.stg_activities` | `gold.dim_diagnosis` |
| `silver.int_doctors` | `gold.dim_doctor` |
| `silver.stg_encounters` | `gold.dim_facility` |
| `silver.stg_facilities` | `gold.dim_facility` |
| `silver.stg_claims` | `gold.dim_health_plan` |
| `silver.stg_health_plans` | `gold.dim_health_plan` |
| `silver.int_patients` | `gold.dim_patient` |
| `silver.int_payers` | `gold.dim_payer` |
| `silver.int_staff` | `gold.dim_staff` |
| `silver.stg_activities` | `gold.fct_claim_activities` |
| `silver.stg_claims` | `gold.fct_claim_activities` |
| `silver.int_patients` | `gold.fct_claims` |
| `silver.int_payers` | `gold.fct_claims` |
| `silver.stg_claims` | `gold.fct_claims` |
| `silver.stg_claims` | `gold.fct_collections` |
| `silver.stg_collections` | `gold.fct_collections` |
| `silver.int_doctors` | `gold.fct_encounters` |
| `silver.int_patients` | `gold.fct_encounters` |
| `silver.stg_encounters` | `gold.fct_encounters` |
| `gold.dim_payer` | `gold.mtr_ar_aging` |
| `gold.fct_claims` | `gold.mtr_ar_aging` |
| `gold.fct_collections` | `gold.mtr_ar_aging` |
| `gold.fct_claims` | `gold.mtr_claims_funnel` |
| `gold.fct_encounters` | `gold.mtr_department_activity` |
| `silver.int_doctors` | `gold.mtr_department_activity` |
| `gold.fct_claims` | `gold.mtr_executive_summary` |
| `gold.fct_collections` | `gold.mtr_executive_summary` |
| `gold.fct_encounters` | `gold.mtr_executive_summary` |
| `silver.stg_claims` | `gold.mtr_executive_summary` |
| `gold.dim_payer` | `gold.mtr_payer_scorecard` |
| `gold.fct_claims` | `gold.mtr_payer_scorecard` |
| `gold.fct_collections` | `gold.mtr_payer_scorecard` |
| `gold.fct_claims` | `gold.mtr_revenue_monthly` |
| `gold.fct_collections` | `gold.mtr_revenue_monthly` |
| `silver.stg_encounters` | `silver.int_doctors` |
| `silver.stg_facilities` | `silver.int_doctors` |
| `silver.stg_users` | `silver.int_doctors` |
| `silver.stg_claims` | `silver.int_patients` |
| `silver.stg_encounters` | `silver.int_patients` |
| `silver.stg_users` | `silver.int_patients` |
| `silver.stg_claims` | `silver.int_payers` |
| `silver.stg_health_plans` | `silver.int_payers` |
| `silver.stg_users` | `silver.int_payers` |
| `silver.stg_users` | `silver.int_staff` |
| `bronze.activities` | `silver.stg_activities` |
| `bronze.claims` | `silver.stg_claims` |
| `bronze.collections` | `silver.stg_collections` |
| `bronze.encounters` | `silver.stg_encounters` |
| `bronze.facilities` | `silver.stg_facilities` |
| `bronze.health_plans` | `silver.stg_health_plans` |
| `bronze.users` | `silver.stg_users` |
