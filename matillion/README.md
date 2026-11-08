# Matillion track: operations notes

Everything needed to stand the Claimwise pipelines up again on Matillion (Maia Foundation, Full SaaS) and Databricks Unity Catalog, and the record of how the project was provisioned.

## Layout

| Path | Purpose |
|---|---|
| `.env` (gitignored, copy `.env.example`) | Databricks host, token, SQL warehouse path, catalog `claimwise` |
| `scripts/dbx.py` | Databricks REST helper: `sql`, `sqlfile`, `put` (no CLI install needed) |
| `scripts/mcp_call.py` | Drive the Matillion MCP server (`@matillion/mcp-server`) from the CLI: `tools`, `describe`, `call` |
| `scripts/dpc_api.py` | Direct Maia Public API calls (OAuth client credentials from the repo-root `.env`, region `us1`) |
| `scripts/maia_task.py`, `scripts/maia_watch.py` | Create and monitor a Maia data-engineer task; `maia_watch.py` auto-approves non-destructive tool calls |
| `sql/00_init.sql` | Catalog, schemas `landing/bronze/silver/gold`, volume `landing.raw` |
| `sql/10_bronze_load.sql` | Typed `CREATE OR REPLACE TABLE ... AS SELECT ... FROM read_files(volume)`; the same statements run inside `10_bronze_load` |
| `sql/90_verify.sql` | Post-run row counts and KPI checks against the As-Is snapshot |
| `lineage/` | Lineage snapshots from Unity Catalog and from Matillion OpenLineage events |
| `porting/` | The brief and guidance Maia received when the dbt project was ported |

## Provisioning record (2026-11-08)

| Object | How | Value |
|---|---|---|
| Databricks catalog | `sql/00_init.sql` | `claimwise` with schemas `landing`, `bronze`, `silver`, `gold`, volume `landing.raw` |
| Landing files | `dbx.py put` | `/Volumes/claimwise/landing/raw/<table>/<table>.csv`, 7 files |
| Matillion project | `POST /v1/projects` `{warehouse: DATABRICKS, agentDeploymentType: FULL_SAAS}` | `claimwise`, id `522addcc-85fa-4237-ba4d-fac5f39c7ea3` |
| Warehouse connection | `POST /v1/projects/{id}/data-platform-connections` `{platformConnectionType: dwh, authProvider: databricks, authType: personal_access_token}` | `claimwise-databricks` |
| Environment | Maia UI (Full SaaS secrets are entered inline there) | `dev`, runner "Maia Hosted Runner", Serverless Starter Warehouse, catalog `claimwise`, schema `bronze` |
| Repository | `POST /v1/projects/{id}/repositories` `{provider: github, providerParameters: {ownerName: senthilsweb}, repositoryName: claimwise}` after installing the Matillion GitHub App | `senthilsweb/claimwise` |
| Build | Maia data-engineer task in PLAN mode, then approved to ACT | branch `claimwise-build`, 4 commits, 35 files |
| First run | `00_claimwise_daily` | SUCCESS, all KPIs match |

## Running the daily pipeline

- **Designer:** switch to the branch, open `pipelines/claimwise/00_claimwise_daily.orch.yaml`, Run.
- **API:** publish the branch as an artifact (`POST /v1/projects/{id}/artifacts`, multipart of the pipeline files, headers `branch`, `commitHash`, `versionName`, `environmentName`) then `POST /v1/projects/{id}/pipeline-executions` with `pipelineName` and `environmentName`. `scripts/dpc_api.py` makes the JSON calls.
- **Verify:** `python3 scripts/dbx.py sqlfile sql/90_verify.sql`.

## Re-running the scaffold

```bash
python3 matillion/scripts/dbx.py sqlfile matillion/sql/00_init.sql
for f in data/landing/*.csv; do t=$(basename "$f" .csv);
  python3 matillion/scripts/dbx.py put "$f" "/Volumes/claimwise/landing/raw/$t/$t.csv"; done
```
