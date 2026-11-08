# Claimwise on Matillion

**Claimwise** is a fictitious healthcare provider at the center of this Healthcare Revenue Cycle Management (RCM) analytics demo. This branch tells the story with **native Matillion pipelines on Databricks Unity Catalog**: synthetic claims data lands as CSV files in a Unity Catalog volume, and Matillion moves and transforms it through bronze, silver, and gold tables, all inside the `claimwise` catalog. No dbt is involved anywhere; the pipelines were built by Maia, Matillion's AI data engineer, from the dbt project that lives on `main`.

```
data/landing/*.csv ─▶ volume claimwise.landing.raw ─▶ bronze (7) ─▶ silver: stg (7) + int (4) ─▶ gold: dims/facts (13) + mtr metrics (6)
                                           every table lives in Unity Catalog catalog `claimwise`
```

| Source system (simulated) | Tables |
|---|---|
| Patient Management (MSSQL) | users, facilities, encounters |
| Claims Processing (Oracle) | claims, claim_activities, collections, health_plans |

## What is in this branch

| Path | Purpose |
|---|---|
| `pipelines/claimwise/` | The Matillion pipelines: 4 orchestrations (`00_claimwise_daily`, `10_bronze_load`, `20_silver`, `30_gold`) and 30 transformation pipelines, one per table |
| `.matillion/maia/rules/claimwise.md` | Context file Maia reads on every prompt in this project: layers, naming, SQL idioms, expected KPIs |
| `data/landing/` | The 7 CSV files that are uploaded to the landing volume (5,000 claims, 8,000 encounters, 24 months) |
| `data-generator/` | Synthetic data generator (Python CLI and Marimo notebook) that produced `data/landing/` |
| `matillion/sql/` | Catalog scaffold, the bronze load SQL executed by `10_bronze_load`, and post-run verification queries |
| `matillion/scripts/` | Helpers: Databricks REST (`dbx.py`), Matillion MCP server (`mcp_call.py`), Public API (`dpc_api.py`), Maia task driver and watcher |
| `matillion/lineage/` | Lineage snapshots from Unity Catalog and from Matillion's OpenLineage feed |
| `matillion/porting/` | The brief and guidance Maia received when the dbt project was ported |

## Quick start

Prerequisites: a Databricks workspace with a SQL warehouse (Free Edition works), a Matillion account in the US region with a Full SaaS runner, the Matillion GitHub App installed on this repository, and Node for the MCP server.

1. Copy `matillion/.env.example` to `matillion/.env` and fill in the Databricks host, token, and warehouse HTTP path. Put `MATILLION_CLIENT_ID` and `MATILLION_CLIENT_SECRET` (Maia profile, API credentials) in a root `.env`. Both files are gitignored.
2. Create the catalog, schemas, and landing volume, then upload the CSVs:
   ```bash
   python3 matillion/scripts/dbx.py sqlfile matillion/sql/00_init.sql
   for f in data/landing/*.csv; do t=$(basename "$f" .csv);
     python3 matillion/scripts/dbx.py put "$f" "/Volumes/claimwise/landing/raw/$t/$t.csv"; done
   ```
3. In Matillion, create a Databricks project on Full SaaS, attach this repository, and add an environment `dev` with a PAT secret, the SQL warehouse, default catalog `claimwise`, default schema `bronze`. The Public API calls used for the project, connection, and repository are in `matillion/README.md`.
4. In Designer switch to this branch, open `pipelines/claimwise/00_claimwise_daily.orch.yaml`, and run it. Or publish and run it from the API with `matillion/scripts/dpc_api.py`.
5. Check the result: `python3 matillion/scripts/dbx.py sqlfile matillion/sql/90_verify.sql`.

## How we ported from dbt to Matillion

The `main` branch holds the original dbt project: seeds for bronze, staging and intermediate models in silver, dimension, fact and metric models in gold, schema tests and ten singular tests. The port kept the data model and every KPI unchanged while removing dbt from the runtime entirely.

**Method.** The dbt model SQL and YAML were treated as the written specification, not as code to run. A context file fixed the conventions (catalog, layers, unquoted identifiers, full-refresh tables, one pipeline per table, stop at gold). A Maia data-engineer task received the context file, the bronze load SQL, every silver and gold model, and the silver test definitions in one prompt, planned the build, and after approval built, ran, validated, and committed each layer. The prompt is kept verbatim in `matillion/porting/maia-brief.md`. Where dbt used Jinja or package macros, the prompt gave the Databricks SQL equivalent, so nothing was left to guesswork.

**Prompting approach, and what we would change.** Matillion's guidance is to keep standing rules in context files (`.matillion/maia/rules/*.md`, 12k characters each) and to send short, scoped prompts, planning first and then acting. This port follows the first half: conventions live in the rules file. The second half was done differently: one large prompt (about 33k characters) covered all seven tables, 34 pipelines and the data quality gates. It worked, with a green run and KPIs matching the dbt snapshot, but it is heavier than recommended. Next time we would send one prompt per layer (bronze, silver, gold), review each plan before Maia acts, and keep the prompts small enough to resume if a task stalls.

**Concept mapping.**

| dbt | Matillion on Databricks |
|---|---|
| `dbt seed` into bronze | CSVs in a Unity Catalog volume, loaded by `CREATE OR REPLACE TABLE ... AS SELECT ... FROM read_files(...)` in SQL Script components (`10_bronze_load`) |
| `source()` / `ref()` | Table Input components reading `claimwise.<schema>.<table>` |
| A model file (`stg_*`, `int_*`, `dim_*`, `fct_*`, `mtr_*`) | One transformation pipeline with the same name, ending in Rewrite Table |
| `dbt build` DAG order | Orchestration pipelines per layer, parallel inside a layer, chained by `00_claimwise_daily` |
| Schema tests (`unique`, `not_null`, `accepted_values`) | Query-to-scalar plus Assert components after silver; a violation fails the run |
| Singular tests in `tests/*.sql` | Query assertions that must return zero rows, after gold |
| `dbt_date.get_date_dimension` | `explode(sequence(...))` date spine in a SQL component |
| `dbt.listagg`, `dbt.datediff`, `dbt.date_trunc` | `array_join(collect_set())`, `datediff()`, `date_trunc('MONTH')` in Calculator expressions |
| `generate_schema_name` macro | Environment default catalog plus explicit schema on each Rewrite Table |
| `dbt docs` lineage graph | Designer lineage view and OpenLineage events, plus Unity Catalog table lineage recorded automatically |
| Elementary, OpenLineage via `dbt-ol` | Matillion's built-in OpenLineage feed and Unity Catalog system tables |

**One defect fixed on the way.** In the dbt project `dim_doctor.sql` was an accidental copy of `dim_diagnosis.sql`. The Matillion `dim_doctor` pipeline builds the doctor dimension from `int_doctors` as intended.

**Verification.** The first full run reproduced the As-Is snapshot of the dbt build exactly:

| Metric | Value |
|---|---|
| Claims / encounters | 5,000 / 8,000 |
| Gross billed | $12,601,107.12 |
| Total collected | $6,050,782.80 |
| Collection rate | 48.02% |
| Denial rate | 14.62% |
| Open AR | $4,729,526.38 |
| Avg. cycle time | 182.8 days |

Claim status mix: Approved 3,054, Denied 731, In Review 598, Submitted 469, Appealed 148.

## Lineage

- **Unity Catalog:** Catalog Explorer, table `claimwise.gold.fct_claims`, Lineage tab. Upstream reaches the CSV files in the landing volume; downstream shows the six metric tables. A Mermaid rendering and edge list are in `matillion/lineage/uc_lineage.md` (37 tables, 59 edges).
- **Matillion:** Designer, project `claimwise`, open `00_claimwise_daily` or any transformation pipeline for the lineage view. The OpenLineage job and dataset table from the first run is in `matillion/lineage/matillion_openlineage.md`.

## Data generator

```bash
pip install -r data-generator/requirements.txt
python data-generator/rcm_module.py --patients 1500 --claims 5000 --encounters 8000 \
  --start-date 2024-08-01 --end-date 2026-07-29 --seed 42 --output-dir data/landing
```

Claim status and collection recovery are weighted, not uniform, so the mix resembles a real RCM book of business. See `data-generator/README.md`.

## License

MIT
