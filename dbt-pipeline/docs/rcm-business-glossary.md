# Healthcare Revenue Cycle Management Business Glossary


## Healthcare Providers Domain
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Provider/Doctor/Physician | Healthcare professional authorized to provide medical services | users.userType='DOCTOR' |
| Specialty | Medical field of expertise for a provider | users.specialty |
| Provider ID | Unique identifier for healthcare provider | users.userID (where userType='DOCTOR') |
| Provider Encounters | Patient visits or consultations performed by provider | encounters where doctorID |

## Patient Care Domain
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Patient | Individual receiving healthcare services | users.userType='PATIENT' |
| Encounter/Visit | Single instance of patient-provider interaction | encounters table |
| Duration of Visit | Time spent during patient encounter (in minutes) | encounters.duration |
| Clinical Notes | Documentation of patient visit observations | encounters.notes |
| Facility | Healthcare location where services are provided | facilities table |

## Billing & Claims Domain
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Claim | Request for payment for healthcare services rendered | claims table |
| Claim Status | Current state of claim in processing cycle | claims.status |
| Diagnosis Code | ICD code identifying patient's medical condition | activities.diagnosisCode |
| Procedure Code | CPT code for specific medical service provided | activities.procedureCode |
| Claim Amount | Monetary value requested for services | claims.amount |
| Collection | Payment received against a claim | collections table |
| Collection Method | Way payment was received (cash, card, etc.) | collections.methodOfCollection |

## Insurance & Payer Domain
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Payer | Insurance company or organization responsible for claim payment | users.userType='PAYER' |
| Health Plan | Specific insurance product offered by payer | health_plans table |
| Plan Name | Identifier for specific insurance coverage type | health_plans.planName |

## Administrative Domain
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Staff | Non-clinical personnel supporting healthcare operations | users.userType='STAFF' |
| Department | Organizational unit within healthcare facility | users.department |
| Role | Staff member's job function | users.role |

## RCM Workflow Domain
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Claim Activity | Actions or events in claim processing lifecycle | activities table |
| Activity Type | Nature of action taken on claim | activities.activityType |
| Activity Date | When claim processing action occurred | activities.activityDate |
| Collection Status | State of payment collection attempt | collections.status |

## Temporal Attributes
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Claim Creation Date | When claim was initially created | claims.dateCreated |
| Claim Update Date | Last modification to claim | claims.dateUpdated |
| Collection Date | When payment was received | collections.date |
| Encounter Date | When patient visit occurred | encounters.date |

## Identifiers
| Business Term | Description | Source Fields |
|--------------|-------------|----------------|
| Business IDs | External reference codes used across systems | *ID fields (userID, claimID, etc.) |
| System IDs | Internal database primary keys | id fields in all tables |
| Encounter ID | Unique identifier for patient visit | encounters.encounterID |
| Collection ID | Unique identifier for payment receipt | collections.collectionID |

# Extended Business Glossary

## Hierarchical Relationships

1. Healthcare Service Delivery Hierarchy
```
Facility
└── Department
    └── Provider
        └── Specialty
            └── Encounter
                ├── Diagnosis
                ├── Procedure
                └── Clinical Notes
```

2. Claims Processing Hierarchy
```
Claim
├── Claim Activities
│   ├── Submission
│   ├── Review
│   ├── Appeal
│   └── Resolution
└── Collections
    ├── Payment Method
    └── Collection Status
```

3. Insurance Structure Hierarchy
```
Payer
└── Health Plan
    ├── Coverage Type
    └── Plan Benefits
```

## Detailed Business Terms with Examples

### Healthcare Provider Domain
| Business Term | Description | Example | Business Process | Related Terms |
|--------------|-------------|---------|------------------|----------------|
| Provider | Healthcare professional authorized to deliver care | Dr. Sarah Smith, Cardiologist | Patient Care, Billing | Specialty, Encounters |
| Specialty | Provider's area of medical expertise | Cardiology, Pediatrics, Orthopedics | Provider Credentialing, Service Planning | Provider, Department |
| Provider Encounters | Patient visits/consultations | 30-minute follow-up cardiology consultation | Patient Care, Scheduling | Patient, Diagnosis |

Example Flow:
```
Dr. Smith (Provider)
├── Specialty: Cardiology
├── Daily Encounters: 12-15 patients
└── Common Procedures: EKG, Stress Test
```

### Patient Care Domain
| Business Term | Description | Example | Business Process | Related Terms |
|--------------|-------------|---------|------------------|----------------|
| Encounter | Patient-provider interaction | Initial consultation for chest pain | Patient Care, Documentation | Provider, Diagnosis |
| Diagnosis Code | ICD-10 code for condition | I21.3 - STEMI | Clinical Documentation, Claims | Claims, Procedures |
| Procedure Code | CPT code for service | 93000 - EKG | Service Delivery, Billing | Claims, Revenue |

Example Flow:
```
Patient Visit
├── Encounter: Initial Cardiology Consultation
├── Diagnosis: I21.3 (STEMI)
├── Procedures: 93000 (EKG)
└── Outcome: Treatment Plan
```

### Revenue Cycle Domain
| Business Term | Description | Example | Business Process | Related Terms |
|--------------|-------------|---------|------------------|----------------|
| Claim | Service payment request | Cardiology consultation claim #12345 | Claims Processing | Encounters, Payments |
| Claim Status | Processing state | "In Review" - Pending payer decision | Claims Management | Activities, Appeals |
| Collection | Payment receipt | $150 copay collected via credit card | Payment Processing | Claims, Revenue |

Example Flow:
```
Claim Lifecycle
├── Creation: Post-encounter billing
├── Processing: Payer review
├── Resolution: Payment/Denial
└── Collection: Payment posting
```

## Business Process Mappings

1. Patient Registration Process
```mermaid
Patient Registration
├── Demographics Collection
├── Insurance Verification
├── Eligibility Check
└── Account Creation
```

2. Clinical Documentation Process
```mermaid
Clinical Documentation
├── Patient History
├── Physical Examination
├── Diagnosis Coding
└── Treatment Planning
```

3. Revenue Cycle Process
```mermaid
Revenue Cycle
├── Service Documentation
├── Charge Capture
├── Claim Submission
├── Payment Processing
└── Revenue Recognition
```

## Process-Term Relationships

1. Pre-Service
- Insurance Verification → Payer, Health Plan
- Eligibility Check → Coverage, Benefits
- Appointment Scheduling → Provider, Department

2. Point-of-Service
- Patient Check-in → Encounter, Facility
- Clinical Documentation → Diagnosis, Procedures
- Charge Capture → Services, Codes

3. Post-Service
- Claim Creation → Encounters, Charges
- Payment Processing → Collections, Adjustments
- Denial Management → Appeals, Resolutions

## Regulatory Mapping

### HIPAA Compliance
| Domain | Requirement | Related Terms | Implementation |
|--------|-------------|---------------|----------------|
| Patient Data | Privacy Rule | Patient Demographics, Clinical Notes | - Data encryption required
| | | | - Access logging mandatory
| | | | - Minimum necessary data exposure
| Medical Records | Security Rule | Encounters, Clinical Documentation | - Secure storage
| | | | - Audit trails
| | | | - Access controls
| Claims | Transaction Rules | Claims, Activities | - Standard formats
| | | | - Electronic transactions
| | | | - Code set standards

### CMS Requirements
| Area | Regulation | Business Terms | Controls |
|------|------------|----------------|-----------|
| Billing | Medicare/Medicaid Rules | Claims, Procedures | - Valid NPI required
| | | | - Correct code usage
| | | | - Documentation requirements
| Documentation | Clinical Notes | Encounters, Diagnoses | - Medical necessity
| | | | - Service documentation
| Payments | Fair Billing | Collections, Charges | - Transparent pricing
| | | | - Patient notification

