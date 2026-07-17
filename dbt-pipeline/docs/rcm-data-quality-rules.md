# Healthcare Revenue Cycle Management Data Quality Rules

### Patient Domain
| Business Term | Quality Rule | Severity | Validation |
|--------------|--------------|----------|------------|
| Patient ID | - Must be unique | Critical | `UNIQUE NOT NULL`
| | - Format: PT[0-9]{6} | High | Pattern match
| Demographics | - DOB cannot be future | Critical | Date validation
| | - Valid contact info | High | Format check
| Insurance | - Valid policy number | Critical | External validation

### Provider Domain
| Business Term | Quality Rule | Severity | Validation |
|--------------|--------------|----------|------------|
| Provider ID | - Must be unique | Critical | `UNIQUE NOT NULL`
| | - Format: DR[0-9]{6} | High | Pattern match
| Specialty | - Must be from approved list | High | Reference check
| NPI | - Valid 10-digit NPI | Critical | Check digit validation

### Claims Domain
| Business Term | Quality Rule | Severity | Validation |
|--------------|--------------|----------|------------|
| Claim ID | - Must be unique | Critical | `UNIQUE NOT NULL`
| | - Format: CLM[0-9]{8} | High | Pattern match
| Diagnosis Codes | - Valid ICD-10 | Critical | Code validation
| | - Active code | High | Date validation
| Procedure Codes | - Valid CPT/HCPCS | Critical | Code validation
| | - Matching specialty | High | Provider-service match
| Amount | - Non-negative | Critical | Value check
| | - Within service limits | High | Range validation

### Collections Domain
| Business Term | Quality Rule | Severity | Monitoring |
|--------------|--------------|----------|------------|
| Collection ID | - Must be unique | Critical | `UNIQUE NOT NULL`
| Amount | - Cannot exceed claim | Critical | Value comparison
| | - Non-negative | Critical | Value check
| Method | - Valid payment type | High | List validation

## Data Quality Monitoring

### Critical Checks
```sql
-- Example: Critical Data Quality Check
WITH validation AS (
    SELECT 
        claim_id,
        amount,
        CASE 
            WHEN amount < 0 THEN 'Invalid Amount'
            WHEN diagnosis_code NOT IN (SELECT code FROM valid_icd10) THEN 'Invalid Diagnosis'
            ELSE 'Valid'
        END as status
    FROM claims
)
SELECT * FROM validation WHERE status != 'Valid'
```

### Business Rule Validation
```sql
-- Example: Business Rule Check
SELECT 
    e.encounter_id,
    e.provider_id,
    p.specialty,
    e.procedure_code
FROM encounters e
JOIN providers p ON e.provider_id = p.id
LEFT JOIN provider_procedure_matrix ppm 
    ON p.specialty = ppm.specialty 
    AND e.procedure_code = ppm.procedure_code
WHERE ppm.procedure_code IS NULL
```

### Monitoring Rules
1. Daily Validation
   - Uniqueness constraints
   - Format validations
   - Code validations

2. Weekly Checks
   - Provider-service matching
   - Payment reconciliation
   - Documentation completeness

3. Monthly Audits
   - Compliance review
   - Pattern analysis
   - Outlier detection

# RCM Data Quality Validation Queries

These queries help:

1. Identify data quality issues
2. Validate business rules
3. Ensure referential integrity
4. Monitor process compliance

## Validation by Domain

### User/Provider/Patient Validations
```sql
-- Check for invalid user types
SELECT DISTINCT "userType"
FROM raw.users
WHERE "userType" NOT IN ('PATIENT', 'DOCTOR', 'STAFF', 'PAYER');

-- Validate Provider Specialties
SELECT u.id, u."userID", u.specialty
FROM raw.users u
WHERE u."userType" = 'DOCTOR' 
  AND (u.specialty IS NULL OR u.specialty = '');

-- Check for duplicate provider IDs
SELECT "userID", COUNT(*)
FROM raw.users
WHERE "userType" = 'DOCTOR'
GROUP BY "userID"
HAVING COUNT(*) > 1;

-- Age validation for patients
SELECT id, "userID", "dateOfBirth"
FROM raw.users
WHERE "userType" = 'PATIENT'
  AND ("dateOfBirth" > CURRENT_DATE 
      OR "dateOfBirth" < '1900-01-01');
```

### Encounter Validations
```sql
-- Check for encounters without valid providers
SELECT e.*
FROM raw.encounters e
LEFT JOIN raw.users u ON e."doctorID" = u.id
WHERE u.id IS NULL OR u."userType" != 'DOCTOR';

-- Validate encounter durations
SELECT *
FROM raw.encounters
WHERE duration <= 0 
   OR duration > 480;  -- assuming max 8 hours

-- Check for future dated encounters
SELECT *
FROM raw.encounters
WHERE date > CURRENT_DATE;

-- Encounters without facility
SELECT e.*
FROM raw.encounters e
LEFT JOIN raw.facilities f ON e."facilityID" = f.id
WHERE f.id IS NULL;
```

### Claims Validations
```sql
-- Claims with invalid amounts
SELECT *
FROM raw.claims
WHERE amount <= 0;

-- Claims with inconsistent dates
SELECT *
FROM raw.claims
WHERE "dateCreated" > "dateUpdated"
   OR "dateCreated" > CURRENT_DATE;

-- Orphaned claims (no patient or payer)
SELECT c.*
FROM raw.claims c
LEFT JOIN raw.users patient ON c."patientID" = patient.id
LEFT JOIN raw.users payer ON c."payerID" = payer.id
WHERE patient.id IS NULL 
   OR payer.id IS NULL;

-- Check claim status validity
SELECT DISTINCT status
FROM raw.claims
WHERE status NOT IN ('Submitted', 'In Review', 'Approved', 'Denied', 'Appealed');
```

### Collection Validations
```sql
-- Collections exceeding claim amount
SELECT 
    c.id as collection_id,
    cl.id as claim_id,
    c."amountCollected",
    cl.amount as claim_amount
FROM raw.collections c
JOIN raw.claims cl ON c."claimID" = cl.id
WHERE c."amountCollected" > cl.amount;

-- Invalid collection methods
SELECT DISTINCT "methodOfCollection"
FROM raw.collections
WHERE "methodOfCollection" NOT IN 
    ('Cash', 'Credit Card', 'Bank Transfer', 'Check', 'Electronic Payment');

-- Collections for non-approved claims
SELECT c.*
FROM raw.collections c
JOIN raw.claims cl ON c."claimID" = cl.id
WHERE cl.status != 'Approved';
```

### Activity Validations
```sql
-- Activities with invalid diagnosis/procedure codes
SELECT *
FROM raw.activities
WHERE ("diagnosisCode" ~ '^ICD-' IS FALSE AND "diagnosisCode" IS NOT NULL)
   OR ("procedureCode" ~ '^CPT-' IS FALSE AND "procedureCode" IS NOT NULL);

-- Activities without valid claims
SELECT a.*
FROM raw.activities a
LEFT JOIN raw.claims c ON a."claimID" = c.id
WHERE c.id IS NULL;

-- Check activity date sequence
SELECT a.*
FROM raw.activities a
JOIN raw.claims c ON a."claimID" = c.id
WHERE a."activityDate" < c."dateCreated"
   OR a."activityDate" > c."dateUpdated";
```

### Cross-Domain Validations
```sql
-- Check referential integrity across all domains
WITH integrity_check AS (
    SELECT 
        (SELECT COUNT(*) FROM raw.encounters e 
         LEFT JOIN raw.users u ON e."patientID" = u.id 
         WHERE u.id IS NULL) as invalid_patient_encounters,
        (SELECT COUNT(*) FROM raw.claims c 
         LEFT JOIN raw.users u ON c."payerID" = u.id 
         WHERE u.id IS NULL) as invalid_payer_claims,
        (SELECT COUNT(*) FROM raw.activities a 
         LEFT JOIN raw.claims c ON a."claimID" = c.id 
         WHERE c.id IS NULL) as orphaned_activities
)
SELECT * FROM integrity_check
WHERE invalid_patient_encounters > 0
   OR invalid_payer_claims > 0
   OR orphaned_activities > 0;

-- Validate complete claim workflow
SELECT 
    c.id as claim_id,
    c.status,
    COUNT(a.id) as activity_count,
    COUNT(col.id) as collection_count
FROM raw.claims c
LEFT JOIN raw.activities a ON c.id = a."claimID"
LEFT JOIN raw.collections col ON c.id = col."claimID"
GROUP BY c.id, c.status
HAVING (c.status = 'Approved' AND COUNT(col.id) = 0)
    OR (c.status != 'Approved' AND COUNT(col.id) > 0);
```

# Analytical Queries for Visualization and Dashboard

## 1. Patient Encounters & Front Office Analytics
```sql
-- Patients by Doctor Department
WITH doctor_departments AS (
    SELECT 
        u.specialty as department,
        COUNT(DISTINCT e."patientID") as patient_count
    FROM raw.encounters e
    JOIN raw.users u ON e."doctorID" = u.id
    WHERE u."userType" = 'DOCTOR'
    GROUP BY u.specialty
    ORDER BY patient_count DESC
)
SELECT 
    department,
    patient_count,
    ROUND(100.0 * patient_count / SUM(patient_count) OVER (), 2) as percentage
FROM doctor_departments;

-- No Show Analysis
SELECT 
    CASE 
        WHEN status = 'DNA' THEN 'No Show'
        ELSE 'Attended'
    END as attendance_status,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM raw.encounters
GROUP BY status;

-- Appointment Mode Distribution
SELECT 
    type as appointment_mode,
    COUNT(*) as count,
    COUNT(CASE WHEN status = 'Attended' THEN 1 END) as attended_count
FROM raw.encounters
GROUP BY type;
```

## 2. Claims and Revenue Analytics
```sql
-- AR Amount by Duration Buckets
WITH ar_buckets AS (
    SELECT 
        CASE 
            WHEN date_part('day', CURRENT_DATE - "dateCreated") <= 30 THEN '0-30'
            WHEN date_part('day', CURRENT_DATE - "dateCreated") <= 60 THEN '31-60'
            WHEN date_part('day', CURRENT_DATE - "dateCreated") <= 90 THEN '61-90'
            WHEN date_part('day', CURRENT_DATE - "dateCreated") <= 120 THEN '91-120'
            ELSE '120+'
        END as ar_bucket,
        amount
    FROM raw.claims
    WHERE status != 'Closed'
)
SELECT 
    ar_bucket,
    COUNT(*) as claim_count,
    SUM(amount) as total_amount
FROM ar_buckets
GROUP BY ar_bucket
ORDER BY ar_bucket;

-- Denial Analysis by Reason
SELECT 
    a."activityType" as denial_reason,
    COUNT(*) as denial_count,
    SUM(c.amount) as denied_amount,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as denial_percentage
FROM raw.claims c
JOIN raw.activities a ON c.id = a."claimID"
WHERE c.status = 'Denied'
GROUP BY a."activityType";

-- AR by Payer and Aging Bucket
WITH payer_ar AS (
    SELECT 
        u.name as payer_name,
        CASE 
            WHEN date_part('day', CURRENT_DATE - c."dateCreated") <= 30 THEN '0-30'
            WHEN date_part('day', CURRENT_DATE - c."dateCreated") <= 60 THEN '31-60'
            WHEN date_part('day', CURRENT_DATE - c."dateCreated") <= 90 THEN '61-90'
            ELSE '90+'
        END as aging_bucket,
        SUM(c.amount) as ar_amount
    FROM raw.claims c
    JOIN raw.users u ON c."payerID" = u.id
    WHERE c.status NOT IN ('Closed', 'Paid')
    GROUP BY u.name, aging_bucket
)
SELECT * FROM payer_ar
PIVOT(SUM(ar_amount) FOR aging_bucket IN ('0-30', '31-60', '61-90', '90+'));
```

## 3. Operational Performance Metrics
```sql
-- Department Volume Analysis
SELECT 
    u.specialty as department,
    COUNT(*) as total_encounters,
    COUNT(DISTINCT e."patientID") as unique_patients,
    COUNT(DISTINCT e."doctorID") as active_doctors,
    ROUND(COUNT(*)::float / COUNT(DISTINCT e."doctorID"), 2) as encounters_per_doctor
FROM raw.encounters e
JOIN raw.users u ON e."doctorID" = u.id
WHERE u."userType" = 'DOCTOR'
GROUP BY u.specialty;

-- Revenue by Department and Facility
SELECT 
    u.specialty as department,
    f.name as facility,
    COUNT(DISTINCT e.id) as encounter_count,
    COUNT(DISTINCT c.id) as claim_count,
    SUM(c.amount) as billed_amount,
    SUM(col."amountCollected") as collected_amount
FROM raw.encounters e
JOIN raw.users u ON e."doctorID" = u.id
JOIN raw.facilities f ON e."facilityID" = f.id
LEFT JOIN raw.claims c ON e."patientID" = c."patientID"
LEFT JOIN raw.collections col ON c.id = col."claimID"
GROUP BY u.specialty, f.name;

-- Collection Performance Trends
SELECT 
    DATE_TRUNC('month', col.date) as collection_month,
    COUNT(DISTINCT col.id) as collection_count,
    SUM(col."amountCollected") as collected_amount,
    ROUND(100.0 * SUM(col."amountCollected") / SUM(c.amount), 2) as collection_rate
FROM raw.collections col
JOIN raw.claims c ON col."claimID" = c.id
GROUP BY collection_month
ORDER BY collection_month;
```

## 4. KPI Dashboard Metrics
```sql
-- Overall RCM Performance Metrics
SELECT 
    COUNT(DISTINCT e.id) as total_encounters,
    COUNT(DISTINCT c.id) as total_claims,
    SUM(c.amount) as total_billed,
    SUM(col."amountCollected") as total_collected,
    ROUND(100.0 * SUM(col."amountCollected") / NULLIF(SUM(c.amount), 0), 2) as collection_rate,
    ROUND(100.0 * COUNT(CASE WHEN c.status = 'Denied' THEN 1 END) / 
          NULLIF(COUNT(c.id), 0), 2) as denial_rate,
    AVG(DATE_PART('day', c."dateUpdated" - c."dateCreated")) as avg_claim_processing_days
FROM raw.encounters e
LEFT JOIN raw.claims c ON e."patientID" = c."patientID"
LEFT JOIN raw.collections col ON c.id = col."claimID";
```
