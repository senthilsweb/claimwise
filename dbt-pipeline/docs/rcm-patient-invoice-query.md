
## Patient Invoice / Medical Bill

A structured document sent to patients detailing services, insurance adjustments, and the amount due.


<img width="1413" alt="image" src="https://github.com/user-attachments/assets/43efa07f-0a3c-44d8-a115-eaec520eb388" />


```sql
SELECT 
    dp.patient_id,
    dp.patient_code,
    dp.patient_name,
    dp.dateOfBirth AS patient_dob,
    dp.contactInfo AS patient_contact,
    
    df.facility_name,
    df.facility_location,
    df.contact_info AS facility_contact,

    fe.encounter_date,
    'CPT-12345' AS service_code, -- Hardcoded CPT Code
    'General Consultation' AS service_description, -- Hardcoded Service Name
    fe.duration_minutes,

    fc.claim_date,
    fc.claim_amount,
    COALESCE(fc.claim_amount * 0.85, 0) AS insurance_payment, -- Assume 85% Insurance Coverage
    (fc.claim_amount - COALESCE(fc.claim_amount * 0.85, 0)) AS patient_responsibility,
    fc.claim_status,

    fp.payer_name,
    fh.plan_name,

    '10%' AS tax, -- Hardcoded tax value
    '0%' AS discount, -- Hardcoded discount value
    (fc.claim_amount - COALESCE(fc.claim_amount * 0.85, 0)) * 1.1 AS total_due -- Including Tax
FROM gold.fct_claims fc
JOIN gold.dim_patient dp ON fc.patient_key = dp.patient_id
JOIN gold.fct_encounters fe ON fc.claim_id = fe.encounter_id
JOIN gold.dim_facility df ON fe.facility_key = df.facility_id
JOIN gold.dim_payer fp ON fc.payer_key = fp.payer_id
JOIN gold.dim_health_plan fh ON fp.payer_id = fh.payer_key
ORDER BY fc.claim_date DESC;
```
