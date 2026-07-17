# macros/generators/generate_model_sql.sql
{% macro generate_model_sql(
    model_name, 
    upstream_model, 
    model_type='staging',
    filter_column=none, 
    filter_value=none
) %}
    {%- set custom_schema = get_custom_schema(model_type) -%}
    {%- set schema_name = generate_schema_name(custom_schema, none) -%}
    {%- set columns = adapter.get_columns_in_relation(ref(upstream_model)) -%}

    {{ config(
        schema=schema_name,
        materialized=materialized_type(model_type)
    ) }}

    WITH source AS (
        SELECT * FROM {{ ref(upstream_model) }}
        {% if filter_column and filter_value %}
        WHERE {{ filter_column }} = '{{ filter_value }}'
        {% endif %}
    ),

    renamed AS (
        SELECT
            {%- for col in columns %}
            {{ process_column_name(col.name, model_type) }}{% if not loop.last %},{% endif %}
            {%- endfor %}
        FROM source
    )

    SELECT 
        *,
        {{ generate_audit_columns() }}
    FROM renamed

{% endmacro %}