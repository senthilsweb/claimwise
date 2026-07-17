# macros/helpers/get_custom_schema.sql
{% macro get_custom_schema(model_type) %}
    {%- if model_type == 'raw' -%}
        raw
    {%- elif model_type == 'staging' -%}
        staging
    {%- elif model_type == 'intermediate' -%}
        intermediate
    {%- elif model_type == 'mart' -%}
        mart
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{% endmacro %}