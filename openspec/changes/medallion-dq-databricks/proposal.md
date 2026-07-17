# Proposal: Medallion Layers, Data-Quality Tests, Generator Alignment, Databricks Enablement

## Why
- Layer names (raw/staging/mart) predated the lakehouse story; the deck and Databricks demo need standard medallion naming.
- The slide deck promised a data-quality framework (daily/weekly checks) that the pipeline didn't implement.
- The synthetic data generator emitted a different schema than the dbt seeds — unusable for pipeline testing.
- The Databricks prod target had never been smoke-tested (no credentials until now); known quoting risk unresolved.

## What Changes
- **Medallion rename**: bronze (seeds/sources) / silver (staging + intermediate) / gold (marts) — schemas, folders, macros, docs, and slide labels.
- **DQ tests from the slide framework**: generic tests (uniqueness, not-null, accepted values) on all silver models plus singular tests for ID formats, referential integrity, provider-specialty matching, documentation completeness, date consistency, and payment reconciliation.
- **Generator rewrite**: `data-generator/rcm_module.py` emits the exact bronze seed schema (camelCase columns, prefixed business IDs, PAYER users, business rules the tests enforce); verified by running the full pipeline on generated data.
- **Databricks enablement** (Free Edition, serverless, catalog `workspace`): fixed local TLS (SSL_CERT_FILE→certifi), removed ALL double-quote identifier quoting (not settable as a session option on serverless; unquoted resolves case-insensitively on DuckDB/Databricks/Snowflake), fixed a seed/build race (`dbt build --exclude-resource-type seed`), added `make rebuild`.
- **Slides**: medallion labels, Databricks icons, Unity Catalog lineage slide with live captures.

## Impact
- Affected specs: `warehouse-targets`, `pipeline-operations` (behavioral deltas: unquoted identifiers, seed exclusion in build)
- Affected code: dbt models/tests/macros/config, `data-generator/`, `slides/`, docs
- Validation: dev (DuckDB) and prod (Databricks) builds green; generator output passes the full test suite end-to-end
