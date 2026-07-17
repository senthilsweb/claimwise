{% macro generate_audit_columns() %}
    current_timestamp as dbt_loaded_at,
    '{{ invocation_id }}' as dbt_batch_id,
    '{{ this.schema }}' as dbt_schema_name,
    '{{ this.name }}' as dbt_model_name,
    '{{ target.name }}' as dbt_target_name
{% endmacro %}