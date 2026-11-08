-- Post-run checks for the Matillion build. Compare with the checked-in As-Is snapshot in README.md.
SELECT 'row_counts' AS check_name, to_json(named_struct(
  'bronze_claims', (SELECT count(*) FROM claimwise.bronze.claims),
  'stg_claims',    (SELECT count(*) FROM claimwise.silver.stg_claims),
  'int_patients',  (SELECT count(*) FROM claimwise.silver.int_patients),
  'fct_claims',    (SELECT count(*) FROM claimwise.gold.fct_claims),
  'fct_encounters',(SELECT count(*) FROM claimwise.gold.fct_encounters),
  'dim_date',      (SELECT count(*) FROM claimwise.gold.dim_date))) AS result;
SELECT 'executive_summary' AS check_name, to_json(struct(*)) AS result FROM claimwise.gold.mtr_executive_summary;
SELECT claim_status, claim_count, pct_of_claims FROM claimwise.gold.mtr_claims_funnel ORDER BY claim_count DESC;
SELECT table_schema, table_name, table_type FROM claimwise.information_schema.tables WHERE table_schema IN ('bronze','silver','gold') ORDER BY 1,2
