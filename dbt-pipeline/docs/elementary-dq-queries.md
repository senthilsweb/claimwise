### DQ Queries

```sql
select
  short_name
  , description
  , quality_dimension
  , concat(schema_name, '.', test_column_name) as fqdn
from
  elementary.dbt_tests
```
