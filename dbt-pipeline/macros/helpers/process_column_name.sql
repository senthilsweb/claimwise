{% macro process_column_name(column_name, model_type) %}
    {%- if model_type == 'staging' -%}
        {{ column_name }} as {{ column_name | lower }}
    {%- elif model_type == 'intermediate' -%}
        {{ column_name }} as {{ column_name | replace('_id', '_key') | lower }}
    {%- elif model_type == 'mart' -%}
        {%- if column_name.endswith('_id') -%}
            {{ column_name }} as {{ column_name | replace('_id', '_key') | lower }}
        {%- else -%}
            {{ column_name }} as {{ column_name | lower }}
        {%- endif -%}
    {%- else -%}
        {{ column_name }}
    {%- endif -%}
{% endmacro %}