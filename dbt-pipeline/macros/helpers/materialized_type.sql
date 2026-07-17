# macros/helpers/materialized_type.sql
{% macro materialized_type(model_type) %}
    {%- if model_type == 'raw' -%}
        table
    {%- elif model_type == 'staging' -%}
        view
    {%- elif model_type == 'intermediate' -%}
        view
    {%- elif model_type == 'mart' -%}
        table
    {%- else -%}
        view
    {%- endif -%}
{% endmacro %}