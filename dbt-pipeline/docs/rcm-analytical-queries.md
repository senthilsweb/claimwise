### Patient encounter analysis

```sql
with patient_metrics as (
    select 
        dp.patient_id,
        dp.patient_name,
        count(fe.encounter_id) as total_encounters,
        sum(fe.emergency_visit_flag) as emergency_visits,
        avg(fe.duration_minutes) as avg_visit_duration
    from "mart"."dim_patient" dp
    left join "mart"."fct_encounters" fe 
        on dp.patient_id = fe.patient_key
    group by 1, 2
)

select * from patient_metrics
where total_encounters > 5
order by emergency_visits desc;
```

### Claims analysis by payer
```sql
select 
    dp.payer_name,
    count(fc.claim_id) as total_claims,
    sum(fc.claim_amount) as total_claim_amount,
    avg(fc.claim_amount) as avg_claim_amount,
    sum(fc.approved_claim_flag) as approved_claims,
    sum(fc.denied_claim_flag) as denied_claims
from "mart"."dim_payer" dp
join "mart"."fct_claims" fc 
    on dp.payer_id = fc.payer_key
group by 1
order by total_claim_amount desc;
```


### Department-wise Patient Volume
```sql
SELECT 
    f.facility_name,
    COUNT(e.encounter_id) as total_encounters,
    COUNT(DISTINCT e.patient_key) as unique_patients,
    SUM(e.encounter_count) as encounter_count
FROM mart.fct_encounters e
JOIN mart.dim_facility f ON e.facility_key = f.facility_id
--JOIN mart.dim_date d ON e.date_key = d.date_id
--WHERE d.year = 2023  -- Assuming we want current year
GROUP BY f.facility_name
ORDER BY total_encounters DESC;
```

### Facility Performance Metrics
```sql
SELECT 
    f.facility_name,
    f.total_patients_served,
    f.total_doctors_practicing,
    COUNT(DISTINCT e.encounter_id) as total_encounters,
    ROUND(COUNT(DISTINCT e.encounter_id)::numeric / 
          NULLIF(f.total_doctors_practicing, 0), 2) as encounters_per_doctor
FROM mart.dim_facility f
LEFT JOIN mart.fct_encounters e ON f.facility_id = e.facility_key
GROUP BY 
    f.facility_name,
    f.total_patients_served,
    f.total_doctors_practicing;
 ```   
 
### Claims Processing Performance
```sql
SELECT 
    p.payer_name,
    COUNT(c.claim_id) as total_claims,
    SUM(c.claim_amount) as total_claim_amount,
    AVG(c.claim_amount) as avg_claim_amount,
    SUM(col.collected_amount) as total_collected,
    AVG(col.collection_rate) as avg_collection_rate
FROM mart.fct_claims c
JOIN mart.dim_payer p ON c.payer_key = p.payer_id
LEFT JOIN mart.fct_collections col ON c.claim_id = col.claim_key
GROUP BY p.payer_name;   
```

### Claim Activity Analysis
```sql
SELECT 
    ca.activity_type,
    COUNT(*) as activity_count,
    COUNT(DISTINCT ca.claim_key) as unique_claims
FROM mart.fct_claim_activities ca
JOIN mart.fct_claims c ON ca.claim_key = c.claim_id
GROUP BY ca.activity_type;
```
    

### Monthly Claims and Collections Trend
```sql
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', c.claim_date) AS month,
        EXTRACT(YEAR FROM c.claim_date) AS year,
        EXTRACT(MONTH FROM c.claim_date) AS month_number,
        TO_CHAR(c.claim_date, 'Month') AS month_name,
        COUNT(c.claim_id) AS claim_count,
        SUM(c.claim_amount) AS total_amount,
        SUM(c.approved_claim_flag) AS approved_claims,
        SUM(c.denied_claim_flag) AS denied_claims,
        SUM(col.collected_amount) AS collected_amount,
        AVG(col.collection_rate) AS avg_collection_rate
    FROM mart.fct_claims c
    LEFT JOIN mart.fct_collections col ON c.claim_id = col.claim_key
    GROUP BY 
        DATE_TRUNC('month', c.claim_date),
        EXTRACT(YEAR FROM c.claim_date),
        EXTRACT(MONTH FROM c.claim_date),
        TO_CHAR(c.claim_date, 'Month')
)
SELECT 
    year,
    month_name,
    claim_count,
    total_amount,
    collected_amount,
    ROUND((COALESCE(collected_amount, 0) / NULLIF(total_amount, 0) * 100)::numeric, 2) AS collection_percentage,
    ROUND((COALESCE(denied_claims, 0)::numeric / NULLIF(claim_count, 0) * 100), 2) AS denial_rate,
    avg_collection_rate
FROM monthly_metrics
ORDER BY year, month_number;
```
