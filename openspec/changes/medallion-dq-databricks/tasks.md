# Tasks (AI-DLC Bolts)

AI-DLC mapping: **Inception** = user request (medallion naming, tests from slide DQ framework, verify dbt + generator) · **Construction** = B1–B4 · **Operations** = B5 live Databricks validation.

## B1. Medallion restructure
- [x] 1.1 Rename layers: seeds→bronze, staging→silver (intermediate under silver), mart→gold — schemas, folders, source defs, macros
- [x] 1.2 Update docs, README, Makefile/entrypoint comments, slide labels/icons

## B2. Data-quality tests (from slide framework)
- [x] 2.1 `_silver_models.yml` generic tests: unique/not_null + accepted values on all 7 staging models
- [x] 2.2 Singular tests: ID formats, referential integrity, provider-specialty, documentation completeness, claim date consistency, collections-for-approved-only

## B3. Generator alignment
- [x] 3.1 Rewrite `rcm_module.py` to the bronze seed schema + business rules; update marimo notebook and README
- [x] 3.2 End-to-end proof: generated data → seed → build → all tests green

## B4. Databricks enablement
- [x] 4.1 TLS fix (SSL_CERT_FILE→certifi in .env); venv with dbt-databricks
- [x] 4.2 De-quote all identifiers (serverless rejects the ANSI double-quote option); `quoting: identifier: false`
- [x] 4.3 Seed/build race fix: `--exclude-resource-type seed` in build/rebuild/daily; `make rebuild` target

## B5. Validation
- [x] 5.1 dev (DuckDB) full build green
- [x] 5.2 prod (Databricks Free Edition serverless) full build green; bronze/silver/gold schemas confirmed
- [x] 5.3 Unity Catalog lineage captured for the deck
