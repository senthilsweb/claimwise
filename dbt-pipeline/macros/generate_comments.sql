{% macro create_table_comment() %}
  {%- set relation = this %}
  {%- set model = model %}
  
  {% if model.description is not none %}
    {% set escaped_comment = model.description | replace("'", "''") %}
    COMMENT ON TABLE {{ relation }} IS E'{{ escaped_comment }}';
  {% endif %}
  
  {% for column in adapter.get_columns_in_relation(relation) %}
    {% set column_model = model.columns[column.name] %}
    {% if column_model.description is not none %}
      {% set escaped_comment = column_model.description | replace("'", "''") %}
      COMMENT ON COLUMN {{ relation }}.{{ column.name }} IS E'{{ escaped_comment }}';
    {% endif %}
  {% endfor %}
{% endmacro %}