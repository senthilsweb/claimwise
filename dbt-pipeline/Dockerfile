# Production runner: dbt + Databricks adapter + Elementary CLI.
# Dev runs bare on DuckDB — this image is only used against Databricks.
FROM python:3.11-slim

WORKDIR /app

# git is needed by dbt deps for git-pinned packages; adapters are pure wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir 'elementary-data[databricks]'

# Project files
COPY dbt_project.yml profiles.yml packages.yml ./
COPY macros/ macros/
COPY models/ models/
COPY seeds/ seeds/
COPY tests/ tests/
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Pre-install dbt packages and prepare writable dirs.
RUN mkdir -p target logs reports dbt_packages \
    && dbt deps --profiles-dir . --project-dir .

ENV DBT_PROFILES_DIR=/app \
    DBT_PROJECT_DIR=/app \
    DBT_TARGET=prod

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["daily"]
