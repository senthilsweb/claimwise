# Conversion guidance given to Maia (dbt project to native Matillion pipelines on Databricks)

This is the guidance that accompanied the build brief (`maia-brief.md`) when the dbt project was ported. It is kept as a record of the port; the pipelines under `pipelines/claimwise/` are now the source of truth.

## Scope of the conversion
- Convert only the dbt models under `models/silver/**/*.sql` and `models/gold/**/*.sql`, their `*.yml` files (column descriptions and tests), and the singular tests under `tests/*.sql`.
- Bronze is not a conversion target: run `matillion/sql/10_bronze_load.sql` verbatim, one SQL Script component per statement, inside orchestration `10_bronze_load`.
- Seeds, macros, packages, profiles and `dbt_project.yml` are out of scope.

## Output
- Three layer orchestrations plus the master `00_claimwise_daily`, under `pipelines/claimwise/`.
- One transformation pipeline per table, named exactly like the table.
- Table and column comments from the `*.yml` descriptions where the component supports them.

## Plan first
Produce the plan before building. Flag for review, do not guess: any Jinja not covered by the translation table, any test that cannot be expressed as a Matillion test, and `dim_doctor` (the dbt file was an accidental copy of `dim_diagnosis`).
