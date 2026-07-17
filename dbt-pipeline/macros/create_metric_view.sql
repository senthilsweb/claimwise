-- Attempt a Unity Catalog metric view over the gold facts. Databricks only;
-- if the platform rejects metric views (e.g. availability on Free Edition),
-- the gold mtr_* models remain the semantic layer of record.
-- Usage: dbt run-operation create_metric_view --target prod
{% macro create_metric_view() %}
    {% if target.type != 'databricks' %}
        {{ exceptions.raise_compiler_error("create_metric_view runs on the Databricks target only (got '" ~ target.type ~ "')") }}
    {% endif %}
    {% set catalog = env_var('DATABRICKS_CATALOG', 'workspace') %}
    {% set sql %}
create or replace view {{ catalog }}.gold.claimwise_metrics
with metrics
language yaml
as $$
version: 0.1
source: {{ catalog }}.gold.fct_claims
dimensions:
  - name: claim_month
    expr: DATE_TRUNC('MONTH', claim_date)
  - name: claim_status
    expr: claim_status
measures:
  - name: total_billed
    expr: SUM(claim_amount)
  - name: claim_count
    expr: COUNT(1)
  - name: avg_claim_amount
    expr: AVG(claim_amount)
  - name: denial_rate_pct
    expr: 100.0 * SUM(denied_claim_flag) / COUNT(1)
$$
    {% endset %}
    {% do run_query(sql) %}
    {{ log("Created metric view " ~ catalog ~ ".gold.claimwise_metrics", info=True) }}
{% endmacro %}
