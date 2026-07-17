## Explanation Of Benefits Statement

A multi page statement sent to patients explaining how their insurance processed the claim

<img width="1475" alt="image" src="https://github.com/user-attachments/assets/58a0fa11-9f86-46eb-92af-459094165daf" />

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

    fe.encounter_date AS service_date,
    fc.claim_date,
    fc.claim_id AS claim_reference,
    fc.claim_amount AS billed_amount,
    
    COALESCE(fc.claim_amount * 0.85, 0) AS insurance_payment, -- Assuming 85% insurance coverage
    (fc.claim_amount - COALESCE(fc.claim_amount * 0.85, 0)) AS patient_responsibility,
    
    'Healthcare360 Member ID: HC360-' || dp.patient_id AS member_id, -- Hardcoded Member ID Format
    'Group Name: Healthcare360 Premium Plan' AS group_name, -- Hardcoded Group Name
    'Group Number: HC360-98765' AS group_number, -- Hardcoded Group Number
    'Deductible Applied: $100' AS deductible, -- Placeholder, can be dynamically calculated
    'Remaining Deductible: $900' AS remaining_deductible, -- Hardcoded
    'Claim Processed' AS claim_status, -- Static placeholder (to be replaced dynamically)

    fp.payer_name,
    fh.plan_name,

    'Your annual benefit balance is $5000. Remaining balance: $3500' AS benefit_balance, -- Placeholder
    'If you disagree with this decision, you may appeal within 30 days.' AS appeal_instruction, -- Hardcoded appeal instructions
    'Customer Service: 1-800-HC360' AS customer_service -- Static contact details
FROM gold.fct_claims fc
JOIN gold.dim_patient dp ON fc.patient_key = dp.patient_id
JOIN gold.fct_encounters fe ON fc.claim_id = fe.encounter_id
JOIN gold.dim_facility df ON fe.facility_key = df.facility_id
JOIN gold.dim_payer fp ON fc.payer_key = fp.payer_id
JOIN gold.dim_health_plan fh ON fp.payer_id = fh.payer_key
ORDER BY fc.claim_date DESC;

```

