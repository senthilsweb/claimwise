# Claimwise Revenue Pulse — Databricks AI/BI Dashboard

Dashboard-as-code: `claimwise-revenue-pulse.lvdash.json` is the source of
truth, deployed with the Databricks SDK. Three pages — Executive Overview,
Claims Operations, Payers & Providers — all querying the gold metric layer
(`gold.mtr_*`), where every KPI is computed once in dbt.

## Deploy

```bash
cd ../dbt-pipeline          # .env holds the Databricks credentials
source .venv/bin/activate
make dashboard              # create-or-update by name, then publish
```

The deploy prints the draft and published URLs. Because widgets query the
gold tables through the SQL warehouse, Unity Catalog lineage shows the
dashboard as a downstream consumer: bronze → silver → gold → dashboard.

## Editing

Edit the JSON and rerun `make dashboard` — the dashboard updates in place at
the same URL. The `__CATALOG__` placeholder is substituted from
`DATABRICKS_CATALOG` at deploy time.
