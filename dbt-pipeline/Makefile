# Healthcare RCM dbt pipeline
# Usage: make <target> [TARGET=dev|prod]

SHELL := /bin/bash
TARGET ?= dev

# Load .env (if present) before every command.
ENV := set -a; [ -f .env ] && . ./.env; set +a;
DBT := $(ENV) dbt

.PHONY: help setup deps debug seed run test build rebuild docs report daily clean clean-db docker-build docker-daily

help:
	@echo "Targets (TARGET=$(TARGET)):"
	@echo "  setup         pip install -r requirements.txt"
	@echo "  deps          dbt deps"
	@echo "  debug         dbt debug"
	@echo "  seed          dbt seed"
	@echo "  run           dbt run"
	@echo "  test          dbt test"
	@echo "  build         dbt build"
	@echo "  rebuild       dbt build --full-refresh"
	@echo "  docs          dbt docs generate"
	@echo "  report        Elementary HTML report -> reports/"
	@echo "  daily         build (+ elementary run & report when TARGET=prod)"
	@echo "  clean         dbt clean + rm target/"
	@echo "  clean-db      remove rcm.duckdb"
	@echo "  docker-build  build the prod runner image"
	@echo "  docker-daily  run the daily job via docker compose"

setup:
	@$(ENV) pip install -r requirements.txt

deps:
	@$(DBT) deps

debug:
	@$(DBT) debug --target $(TARGET)

seed:
	@$(DBT) seed --target $(TARGET)

run:
	@$(DBT) run --target $(TARGET)

test:
	@$(DBT) test --target $(TARGET)

# seed runs first: silver models read seeds as sources (no DAG edge), so a
# fresh database needs the bronze tables loaded before dbt build. Seeds are
# then excluded from build itself — re-running them there races the silver
# CTAS statements (no DAG edge means no ordering) and can capture an empty
# source table mid-reload.
build: seed
	@$(DBT) build --exclude-resource-type seed --target $(TARGET)

# full-refresh: recreate all tables and incremental models from scratch
rebuild: seed
	@$(DBT) build --exclude-resource-type seed --full-refresh --target $(TARGET)

# deploy + publish the AI/BI dashboard (prod/Databricks only)
dashboard:
	@$(ENV) python ../dashboards/deploy.py

# attempt the Unity Catalog metric view (prod only; mtr_* models are the
# semantic layer of record either way)
metricview:
	@$(DBT) run-operation create_metric_view --target prod

docs:
	@$(DBT) docs generate --target $(TARGET)

report:
	@mkdir -p reports
	@$(ENV) edr report --profiles-dir . --profile-target $(TARGET) --file-path reports/elementary_report.html

daily: build
	@if [ "$(TARGET)" = "prod" ]; then \
		$(DBT) run --select elementary --target $(TARGET) && \
		$(MAKE) TARGET=$(TARGET) report; \
	else \
		echo "daily: skipping Elementary (TARGET=$(TARGET))"; \
	fi

clean:
	@$(DBT) clean || true
	@rm -rf target

clean-db:
	@rm -f rcm.duckdb

docker-build:
	@docker build -t healthcare-rcm-dbt .

docker-daily:
	@docker compose run --rm dbt daily
