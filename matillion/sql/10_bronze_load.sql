-- Bronze: load each landed CSV 1:1 into a typed Delta table. Full reload, idempotent.
-- This is the SQL the Matillion bronze orchestration pipeline executes (one SQL Script
-- component per table) so that Unity Catalog records volume -> bronze lineage.
CREATE OR REPLACE TABLE claimwise.bronze.users COMMENT 'All system actors: patients, doctors, staff, payers (source: Patient Management, MSSQL)' AS
SELECT CAST(id AS INT) AS id, userID, userType, name, CAST(dateOfBirth AS DATE) AS dateOfBirth,
       contactInfo, specialty, department, role
FROM read_files('/Volumes/claimwise/landing/raw/users/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.facilities COMMENT 'Healthcare facilities (source: Patient Management, MSSQL)' AS
SELECT CAST(id AS INT) AS id, facilityID, name, location, contactInfo
FROM read_files('/Volumes/claimwise/landing/raw/facilities/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.encounters COMMENT 'Patient encounters / visits (source: Patient Management, MSSQL)' AS
SELECT CAST(id AS INT) AS id, encounterID, CAST(patientID AS INT) AS patientID, CAST(doctorID AS INT) AS doctorID,
       CAST(facilityID AS INT) AS facilityID, CAST(date AS DATE) AS date, type, CAST(duration AS INT) AS duration, notes
FROM read_files('/Volumes/claimwise/landing/raw/encounters/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.health_plans COMMENT 'Insurance plans offered by payers (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, healthPlanID, planName, CAST(payerID AS INT) AS payerID
FROM read_files('/Volumes/claimwise/landing/raw/health_plans/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.claims COMMENT 'Medical claims and their lifecycle status (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, claimID, CAST(patientID AS INT) AS patientID, CAST(payerID AS INT) AS payerID, status,
       CAST(dateCreated AS DATE) AS dateCreated, CAST(dateUpdated AS DATE) AS dateUpdated, CAST(amount AS DOUBLE) AS amount
FROM read_files('/Volumes/claimwise/landing/raw/claims/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.activities COMMENT 'Claim lifecycle activities and events (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, activityID, CAST(claimID AS INT) AS claimID, CAST(activityDate AS DATE) AS activityDate,
       activityType, diagnosisCode, procedureCode, notes
FROM read_files('/Volumes/claimwise/landing/raw/activities/', format => 'csv', header => true, inferColumnTypes => false);

CREATE OR REPLACE TABLE claimwise.bronze.collections COMMENT 'Payment collections against claims (source: Claims Processing, Oracle)' AS
SELECT CAST(id AS INT) AS id, collectionID, CAST(claimID AS INT) AS claimID, CAST(date AS DATE) AS date,
       methodOfCollection, CAST(amountCollected AS DOUBLE) AS amountCollected, status
FROM read_files('/Volumes/claimwise/landing/raw/collections/', format => 'csv', header => true, inferColumnTypes => false)
