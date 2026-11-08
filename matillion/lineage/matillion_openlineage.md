# Matillion OpenLineage events for the first `00_claimwise_daily` run

Emitted by Maia Foundation (producer https://www.matillion.com) for run 01a1bbbf-1053-7245-8bbd-cbc1efb7c58f on 2026-11-08, read through the Public API (`get-lineage-events`).
98 events, 34 jobs. The same graph is shown in Designer: open a pipeline and choose the lineage view.

| job (pipeline) | event types | inputs | outputs |
|---|---|---|---|
| `00_claimwise_daily.orch.yaml` | COMPLETE, START | — | — |
| `10_bronze_load.orch.yaml` | COMPLETE, START | — | — |
| `20_silver.orch.yaml` | COMPLETE, START | — | — |
| `stg_users.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.users | claimwise.silver.stg_users |
| `stg_facilities.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.facilities | claimwise.silver.stg_facilities |
| `stg_encounters.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.encounters | claimwise.silver.stg_encounters |
| `stg_claims.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.claims | claimwise.silver.stg_claims |
| `stg_health_plans.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.health_plans | claimwise.silver.stg_health_plans |
| `stg_collections.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.collections | claimwise.silver.stg_collections |
| `stg_activities.tran.yaml` | COMPLETE, RUNNING, START | claimwise.bronze.activities | claimwise.silver.stg_activities |
| `int_patients.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_claims<br>claimwise.silver.stg_encounters<br>claimwise.silver.stg_users | claimwise.silver.int_patients |
| `int_doctors.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_encounters<br>claimwise.silver.stg_facilities<br>claimwise.silver.stg_users | claimwise.silver.int_doctors |
| `int_staff.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_users | claimwise.silver.int_staff |
| `int_payers.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_claims<br>claimwise.silver.stg_health_plans<br>claimwise.silver.stg_users | claimwise.silver.int_payers |
| `30_gold.orch.yaml` | COMPLETE, START | — | — |
| `dim_facility.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_encounters<br>claimwise.silver.stg_facilities | claimwise.gold.dim_facility |
| `dim_date.tran.yaml` | COMPLETE, RUNNING, START | — | claimwise.gold.dim_date |
| `dim_department.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_users | claimwise.gold.dim_department |
| `dim_diagnosis.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_activities | claimwise.gold.dim_diagnosis |
| `fct_encounters.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.int_doctors<br>claimwise.silver.int_patients<br>claimwise.silver.stg_encounters | claimwise.gold.fct_encounters |
| `dim_payer.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.int_payers | claimwise.gold.dim_payer |
| `fct_collections.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_claims<br>claimwise.silver.stg_collections | claimwise.gold.fct_collections |
| `dim_patient.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.int_patients | claimwise.gold.dim_patient |
| `dim_health_plan.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_claims<br>claimwise.silver.stg_health_plans | claimwise.gold.dim_health_plan |
| `fct_claim_activities.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.stg_activities<br>claimwise.silver.stg_claims | claimwise.gold.fct_claim_activities |
| `dim_doctor.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.int_doctors | claimwise.gold.dim_doctor |
| `fct_claims.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.int_patients<br>claimwise.silver.int_payers<br>claimwise.silver.stg_claims | claimwise.gold.fct_claims |
| `dim_staff.tran.yaml` | COMPLETE, RUNNING, START | claimwise.silver.int_staff | claimwise.gold.dim_staff |
| `mtr_executive_summary.tran.yaml` | COMPLETE, RUNNING, START | claimwise.gold.fct_claims<br>claimwise.gold.fct_collections<br>claimwise.gold.fct_encounters<br>claimwise.silver.stg_claims | claimwise.gold.mtr_executive_summary |
| `mtr_claims_funnel.tran.yaml` | COMPLETE, RUNNING, START | claimwise.gold.fct_claims | claimwise.gold.mtr_claims_funnel |
| `mtr_revenue_monthly.tran.yaml` | COMPLETE, RUNNING, START | claimwise.gold.fct_claims<br>claimwise.gold.fct_collections | claimwise.gold.mtr_revenue_monthly |
| `mtr_payer_scorecard.tran.yaml` | COMPLETE, RUNNING, START | claimwise.gold.dim_payer<br>claimwise.gold.fct_claims<br>claimwise.gold.fct_collections | claimwise.gold.mtr_payer_scorecard |
| `mtr_ar_aging.tran.yaml` | COMPLETE, RUNNING, START | claimwise.gold.dim_payer<br>claimwise.gold.fct_claims<br>claimwise.gold.fct_collections | claimwise.gold.mtr_ar_aging |
| `mtr_department_activity.tran.yaml` | COMPLETE, RUNNING, START | claimwise.gold.fct_encounters<br>claimwise.silver.int_doctors | claimwise.gold.mtr_department_activity |
