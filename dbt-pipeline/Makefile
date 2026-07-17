# Healthcare RCM dbt pipeline
# Usage: make <target> [TARGET=dev|prod]

SHELL := /bin/bash
TARGET ?= dev

# Load .env (if present) before every command.
ENV := set -a; [ -f .env ] && . ./.env; set +a;
DBT := $(ENV) dbt

.PHONY: help setup deps debug seed run test build docs report daily clean clean-db docker-build docker-daily

help:
	@echo "Targets (TARGET=$(TARGET)):"
	@echo "  setup         pip install -r requirements.txt"
	@echo "  deps          dbt deps"
	@echo "  debug         dbt debug"
	@echo "  seed          dbt seed"
	@echo "  run           dbt run"
	@echo "  test          dbt test"
	@echo "  build         dbt build"
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

# seed runs first: staging models read seeds as sources (no DAG edge),
# so a fresh database needs the raw tables loaded before dbt build.
build: seed
	@$(DBT) build --target $(TARGET)

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
