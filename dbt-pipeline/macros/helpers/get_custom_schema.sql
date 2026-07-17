# macros/helpers/get_custom_schema.sql
{% macro get_custom_schema(model_type) %}
    {%- if model_type == 'bronze' -%}
        bronze
    {%- elif model_type == 'silver' -%}
        silver
    {%- elif model_type == 'gold' -%}
        gold
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{% endmacro %}
