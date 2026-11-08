-- Claimwise lakehouse scaffold for the Matillion (Maia) track. Idempotent.
-- Run: python matillion/scripts/dbx.py sqlfile matillion/sql/00_init.sql
CREATE CATALOG IF NOT EXISTS claimwise COMMENT 'Claimwise healthcare RCM demo, built with Matillion Maia (no dbt)';
CREATE SCHEMA IF NOT EXISTS claimwise.landing COMMENT 'Raw CSV files as landed from the source systems (volume only, no tables)';
CREATE SCHEMA IF NOT EXISTS claimwise.bronze  COMMENT 'Raw tables loaded 1:1 from landing CSVs';
CREATE SCHEMA IF NOT EXISTS claimwise.silver  COMMENT 'Staging (stg_*) and intermediate (int_*) tables';
CREATE SCHEMA IF NOT EXISTS claimwise.gold    COMMENT 'Dimensions, facts and metric tables';
CREATE VOLUME IF NOT EXISTS claimwise.landing.raw COMMENT 'Landing zone: one folder per source table';
SHOW SCHEMAS IN claimwise
