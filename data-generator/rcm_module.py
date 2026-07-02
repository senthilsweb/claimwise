"""
RCM Synthetic Data Generator Module

Generates realistic healthcare revenue cycle management (RCM) data
for testing, demos, and development purposes.
"""

import os
import random
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

try:
    import pandas as pd
    from faker import Faker
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install pandas faker pyarrow duckdb")
    raise

# Optional DuckDB import
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


@dataclass
class GeneratorConfig:
    """Configuration for data generation volumes and parameters."""
    num_patients: int = 100
    num_doctors: int = 20
    num_staff: int = 15
    num_facilities: int = 10
    num_encounters: int = 200
    num_claims: int = 300
    avg_activities_per_claim: int = 3
    start_date: datetime = field(default_factory=lambda: datetime.now() - timedelta(days=365))
    end_date: datetime = field(default_factory=datetime.now)
    output_format: str = "csv"
    output_dir: str = "./output"
    duckdb_path: str = "./output/rcm.duckdb"
    seed: Optional[int] = None

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "GeneratorConfig":
        """Create config from dictionary."""
        return cls(
            num_patients=config.get("num_patients", 100),
            num_doctors=config.get("num_doctors", 20),
            num_staff=config.get("num_staff", 15),
            num_facilities=config.get("num_facilities", 10),
            num_encounters=config.get("num_encounters", 200),
            num_claims=config.get("num_claims", 300),
            avg_activities_per_claim=config.get("avg_activities_per_claim", 3),
            start_date=config.get("start_date", datetime.now() - timedelta(days=365)),
            end_date=config.get("end_date", datetime.now()),
            output_format=config.get("output_format", "csv"),
            output_dir=config.get("output_dir", "./output"),
            duckdb_path=config.get("duckdb_path", "./output/rcm.duckdb"),
            seed=config.get("seed"),
        )


class HealthcareDataGenerator:
    """
    Generates synthetic healthcare RCM data with configurable volumes.

    Datasets generated:
    - users: Doctors, staff, and patients
    - facilities: Healthcare facilities
    - health_plans: Insurance plans
    - encounters: Patient visits
    - claims: Medical claims
    - claim_activities: Claim lifecycle events
    - collections: Payment collections
    """

    # Domain constants
    SPECIALTIES = [
        "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology",
        "Dermatology", "Gastroenterology", "Pulmonology", "Endocrinology",
        "Nephrology", "Rheumatology", "Urology", "Psychiatry", "Radiology",
        "Emergency Medicine", "Family Medicine", "Internal Medicine"
    ]

    FACILITY_TYPES = [
        "Hospital", "Clinic", "Urgent Care", "Specialty Center",
        "Ambulatory Surgery Center", "Rehabilitation Center"
    ]

    PAYERS = [
        "Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna",
        "Humana", "Kaiser Permanente", "Anthem", "Centene", "Molina",
        "Medicare", "Medicaid"
    ]

    PLAN_TYPES = ["HMO", "PPO", "EPO", "POS", "HDHP", "Medicare Advantage"]

    ENCOUNTER_TYPES = [
        "Office Visit", "Emergency", "Inpatient", "Outpatient",
        "Telehealth", "Lab Visit", "Imaging", "Procedure"
    ]

    DIAGNOSIS_CODES = [
        "E11.9", "I10", "J06.9", "M54.5", "K21.0", "F32.9", "J45.909",
        "E78.5", "N39.0", "R10.9", "G43.909", "L30.9", "H10.9", "R05.9"
    ]

    CPT_CODES = [
        ("99213", 75.00, 150.00), ("99214", 100.00, 200.00),
        ("99215", 150.00, 300.00), ("99203", 100.00, 200.00),
        ("99204", 150.00, 300.00), ("99205", 200.00, 400.00),
        ("36415", 10.00, 25.00), ("85025", 15.00, 50.00),
        ("80053", 20.00, 75.00), ("71046", 50.00, 150.00),
        ("93000", 50.00, 150.00), ("81001", 10.00, 30.00)
    ]

    CLAIM_STATUSES = [
        "Submitted", "Pending", "Approved", "Denied", "Paid",
        "Partially Paid", "Under Review", "Appealed"
    ]

    CLAIM_ACTIONS = [
        "Submitted", "Acknowledged", "Processed", "Approved",
        "Denied", "Appealed", "Resubmitted", "Paid", "Adjusted"
    ]

    DENIAL_REASONS = [
        "Missing Information", "Invalid Code", "Not Covered",
        "Pre-authorization Required", "Duplicate Claim",
        "Out of Network", "Timely Filing", "Coordination of Benefits"
    ]

    def __init__(self, config: Dict[str, Any] | GeneratorConfig):
        """Initialize generator with configuration."""
        if isinstance(config, dict):
            self.config = GeneratorConfig.from_dict(config)
        else:
            self.config = config

        self.fake = Faker()
        if self.config.seed:
            Faker.seed(self.config.seed)
            random.seed(self.config.seed)

        # Data containers
        self.users: List[Dict] = []
        self.facilities: List[Dict] = []
        self.health_plans: List[Dict] = []
        self.encounters: List[Dict] = []
        self.claims: List[Dict] = []
        self.claim_activities: List[Dict] = []
        self.collections: List[Dict] = []

        # ID tracking
        self.patient_ids: List[int] = []
        self.doctor_ids: List[int] = []

    def _random_date(self, start: datetime = None, end: datetime = None) -> datetime:
        """Generate random date within range."""
        start = start or self.config.start_date
        end = end or self.config.end_date
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        delta = end - start
        random_days = random.randint(0, max(0, delta.days))
        return start + timedelta(days=random_days)

    def generate_users(self) -> List[Dict]:
        """Generate users: doctors, staff, and patients."""
        self.users = []
        user_id = 1

        # Generate doctors
        for _ in range(self.config.num_doctors):
            user = {
                "user_id": user_id,
                "role": "Doctor",
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "email": self.fake.email(),
                "phone": self.fake.phone_number(),
                "specialty": random.choice(self.SPECIALTIES),
                "npi": self.fake.numerify("##########"),
                "license_number": self.fake.bothify("??######"),
                "hire_date": self.fake.date_between(start_date="-10y", end_date="-1y").isoformat(),
                "status": "Active",
                "created_at": datetime.now().isoformat(),
            }
            self.users.append(user)
            self.doctor_ids.append(user_id)
            user_id += 1

        # Generate staff
        staff_roles = ["Nurse", "Admin", "Billing Specialist", "Medical Assistant", "Receptionist"]
        for _ in range(self.config.num_staff):
            user = {
                "user_id": user_id,
                "role": random.choice(staff_roles),
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "email": self.fake.email(),
                "phone": self.fake.phone_number(),
                "specialty": None,
                "npi": None,
                "license_number": None,
                "hire_date": self.fake.date_between(start_date="-10y", end_date="-1y").isoformat(),
                "status": "Active",
                "created_at": datetime.now().isoformat(),
            }
            self.users.append(user)
            user_id += 1

        # Generate patients
        for _ in range(self.config.num_patients):
            user = {
                "user_id": user_id,
                "role": "Patient",
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "email": self.fake.email(),
                "phone": self.fake.phone_number(),
                "specialty": None,
                "npi": None,
                "license_number": None,
                "hire_date": None,
                "status": "Active",
                "created_at": datetime.now().isoformat(),
                "date_of_birth": self.fake.date_of_birth(minimum_age=1, maximum_age=90).isoformat(),
                "gender": random.choice(["Male", "Female", "Other"]),
                "address": self.fake.address().replace("\n", ", "),
                "ssn_last4": self.fake.numerify("####"),
                "mrn": self.fake.numerify("MRN######"),
            }
            self.users.append(user)
            self.patient_ids.append(user_id)
            user_id += 1

        return self.users

    def generate_facilities(self) -> List[Dict]:
        """Generate healthcare facilities."""
        self.facilities = []

        for i in range(1, self.config.num_facilities + 1):
            facility_type = random.choice(self.FACILITY_TYPES)
            facility = {
                "facility_id": i,
                "name": f"{self.fake.company()} {facility_type}",
                "type": facility_type,
                "address": self.fake.street_address(),
                "city": self.fake.city(),
                "state": self.fake.state_abbr(),
                "zip_code": self.fake.zipcode(),
                "phone": self.fake.phone_number(),
                "npi": self.fake.numerify("##########"),
                "tax_id": self.fake.numerify("##-#######"),
                "bed_count": random.randint(10, 500) if facility_type == "Hospital" else None,
                "status": "Active",
                "created_at": datetime.now().isoformat(),
            }
            self.facilities.append(facility)

        return self.facilities

    def generate_health_plans(self) -> List[Dict]:
        """Generate health insurance plans."""
        self.health_plans = []
        plan_id = 1

        for payer in self.PAYERS:
            # Each payer has 1-3 plan types
            num_plans = random.randint(1, 3)
            for _ in range(num_plans):
                plan_type = random.choice(self.PLAN_TYPES)
                plan = {
                    "plan_id": plan_id,
                    "payer_name": payer,
                    "plan_name": f"{payer} {plan_type}",
                    "plan_type": plan_type,
                    "group_number": self.fake.numerify("GRP######"),
                    "deductible": random.choice([500, 1000, 1500, 2000, 2500, 3000]),
                    "copay": random.choice([10, 20, 25, 30, 40, 50]),
                    "coinsurance": random.choice([10, 20, 30]),
                    "out_of_pocket_max": random.choice([3000, 5000, 6500, 8000, 10000]),
                    "effective_date": self.fake.date_between(start_date="-2y", end_date="-1y").isoformat(),
                    "status": "Active",
                    "created_at": datetime.now().isoformat(),
                }
                self.health_plans.append(plan)
                plan_id += 1

        return self.health_plans

    def generate_encounters(self) -> List[Dict]:
        """Generate patient encounters."""
        if not self.patient_ids or not self.doctor_ids:
            raise ValueError("Must generate users before encounters")
        if not self.facilities:
            raise ValueError("Must generate facilities before encounters")

        self.encounters = []

        for i in range(1, self.config.num_encounters + 1):
            encounter_date = self._random_date()
            encounter_type = random.choice(self.ENCOUNTER_TYPES)

            encounter = {
                "encounter_id": i,
                "patient_id": random.choice(self.patient_ids),
                "provider_id": random.choice(self.doctor_ids),
                "facility_id": random.choice([f["facility_id"] for f in self.facilities]),
                "encounter_type": encounter_type,
                "encounter_date": encounter_date.isoformat(),
                "check_in_time": encounter_date.replace(
                    hour=random.randint(7, 17),
                    minute=random.randint(0, 59)
                ).isoformat(),
                "check_out_time": encounter_date.replace(
                    hour=random.randint(8, 20),
                    minute=random.randint(0, 59)
                ).isoformat(),
                "chief_complaint": self.fake.sentence(nb_words=5),
                "diagnosis_code": random.choice(self.DIAGNOSIS_CODES),
                "diagnosis_description": self.fake.sentence(nb_words=4),
                "status": random.choice(["Completed", "In Progress", "Cancelled", "No Show"]),
                "notes": self.fake.paragraph(nb_sentences=2) if random.random() > 0.5 else None,
                "created_at": datetime.now().isoformat(),
            }
            self.encounters.append(encounter)

        return self.encounters

    def generate_claims(self) -> List[Dict]:
        """Generate medical claims."""
        if not self.encounters:
            raise ValueError("Must generate encounters before claims")
        if not self.health_plans:
            raise ValueError("Must generate health_plans before claims")

        self.claims = []

        for i in range(1, self.config.num_claims + 1):
            encounter = random.choice(self.encounters)
            cpt_code, min_charge, max_charge = random.choice(self.CPT_CODES)
            billed_amount = round(random.uniform(min_charge, max_charge), 2)
            allowed_amount = round(billed_amount * random.uniform(0.6, 0.9), 2)

            status = random.choice(self.CLAIM_STATUSES)
            paid_amount = 0.0
            if status in ["Paid", "Partially Paid"]:
                paid_amount = round(allowed_amount * random.uniform(0.5, 1.0), 2)

            encounter_date = datetime.fromisoformat(encounter["encounter_date"])
            submission_date = encounter_date + timedelta(days=random.randint(1, 14))

            claim = {
                "claim_id": i,
                "encounter_id": encounter["encounter_id"],
                "patient_id": encounter["patient_id"],
                "provider_id": encounter["provider_id"],
                "facility_id": encounter["facility_id"],
                "plan_id": random.choice([p["plan_id"] for p in self.health_plans]),
                "claim_number": self.fake.bothify("CLM#########"),
                "cpt_code": cpt_code,
                "diagnosis_code": encounter["diagnosis_code"],
                "service_date": encounter["encounter_date"],
                "submission_date": submission_date.isoformat(),
                "billed_amount": billed_amount,
                "allowed_amount": allowed_amount,
                "paid_amount": paid_amount,
                "patient_responsibility": round(billed_amount - paid_amount, 2),
                "status": status,
                "denial_reason": random.choice(self.DENIAL_REASONS) if status == "Denied" else None,
                "created_at": datetime.now().isoformat(),
            }
            self.claims.append(claim)

        return self.claims

    def generate_claim_activities(self) -> List[Dict]:
        """Generate claim lifecycle activities."""
        if not self.claims:
            raise ValueError("Must generate claims before activities")

        self.claim_activities = []
        activity_id = 1

        for claim in self.claims:
            submission_date = datetime.fromisoformat(claim["submission_date"])
            num_activities = random.randint(1, self.config.avg_activities_per_claim * 2)

            current_date = submission_date
            for j in range(num_activities):
                action = self.CLAIM_ACTIONS[min(j, len(self.CLAIM_ACTIONS) - 1)]

                activity = {
                    "activity_id": activity_id,
                    "claim_id": claim["claim_id"],
                    "action": action,
                    "action_date": current_date.isoformat(),
                    "performed_by": f"User_{random.randint(1, self.config.num_staff)}",
                    "notes": self.fake.sentence() if random.random() > 0.7 else None,
                    "previous_status": self.CLAIM_STATUSES[max(0, j - 1)] if j > 0 else None,
                    "new_status": random.choice(self.CLAIM_STATUSES),
                    "created_at": datetime.now().isoformat(),
                }
                self.claim_activities.append(activity)
                activity_id += 1
                current_date += timedelta(days=random.randint(1, 7))

        return self.claim_activities

    def generate_collections(self) -> List[Dict]:
        """Generate payment collections."""
        if not self.claims:
            raise ValueError("Must generate claims before collections")

        self.collections = []
        collection_id = 1

        # Only create collections for paid or partially paid claims
        paid_claims = [c for c in self.claims if c["status"] in ["Paid", "Partially Paid"]]

        for claim in paid_claims:
            service_date = datetime.fromisoformat(claim["service_date"])
            collection_date = service_date + timedelta(days=random.randint(30, 90))

            collection = {
                "collection_id": collection_id,
                "claim_id": claim["claim_id"],
                "patient_id": claim["patient_id"],
                "amount_billed": claim["patient_responsibility"],
                "amount_collected": round(claim["patient_responsibility"] * random.uniform(0.5, 1.0), 2),
                "collection_date": collection_date.isoformat(),
                "payment_method": random.choice(["Credit Card", "Check", "Cash", "ACH", "Payment Plan"]),
                "payment_reference": self.fake.bothify("PAY########"),
                "status": random.choice(["Collected", "Partial", "Outstanding", "Written Off"]),
                "notes": self.fake.sentence() if random.random() > 0.8 else None,
                "created_at": datetime.now().isoformat(),
            }
            self.collections.append(collection)
            collection_id += 1

        return self.collections

    def generate_all(self) -> Dict[str, int]:
        """Generate all datasets and save to output directory."""
        print("Generating RCM synthetic data...")

        # Generate data in dependency order
        print("  - Generating users...")
        self.generate_users()

        print("  - Generating facilities...")
        self.generate_facilities()

        print("  - Generating health plans...")
        self.generate_health_plans()

        print("  - Generating encounters...")
        self.generate_encounters()

        print("  - Generating claims...")
        self.generate_claims()

        print("  - Generating claim activities...")
        self.generate_claim_activities()

        print("  - Generating collections...")
        self.generate_collections()

        # Save to files
        self._save_all()

        # Return record counts
        return {
            "users": len(self.users),
            "facilities": len(self.facilities),
            "health_plans": len(self.health_plans),
            "encounters": len(self.encounters),
            "claims": len(self.claims),
            "claim_activities": len(self.claim_activities),
            "collections": len(self.collections),
        }

    def _save_all(self):
        """Save all datasets to files or DuckDB."""
        os.makedirs(self.config.output_dir, exist_ok=True)

        datasets = {
            "users": self.users,
            "facilities": self.facilities,
            "health_plans": self.health_plans,
            "encounters": self.encounters,
            "claims": self.claims,
            "claim_activities": self.claim_activities,
            "collections": self.collections,
        }

        fmt = self.config.output_format

        if fmt == "duckdb":
            self._save_to_duckdb(datasets)
        else:
            print(f"\nSaving files to {self.config.output_dir}/ ({fmt} format)...")

            for name, data in datasets.items():
                df = pd.DataFrame(data)
                filepath = os.path.join(self.config.output_dir, f"{name}.{fmt}")

                if fmt == "csv":
                    df.to_csv(filepath, index=False)
                elif fmt == "parquet":
                    df.to_parquet(filepath, index=False)
                elif fmt == "json":
                    df.to_json(filepath, orient="records", indent=2)
                else:
                    raise ValueError(f"Unsupported format: {fmt}")

                print(f"  - {name}.{fmt}: {len(data)} records")

        print("\nData generation complete!")

    def _save_to_duckdb(self, datasets: Dict[str, List[Dict]]):
        """
        Save datasets to DuckDB with three schemas simulating source systems.

        Schemas:
        - patient_mgmt (MSSQL): users, facilities, encounters
        - claims_proc (Oracle): claims, claim_activities, collections, health_plans
        - s3_landing (S3 Raw): all tables as raw landing zone
        """
        if not DUCKDB_AVAILABLE:
            raise ImportError("DuckDB not installed. Run: pip install duckdb")

        db_path = self.config.duckdb_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

        print(f"\nSaving to DuckDB: {db_path}")

        # Schema mapping - which tables go to which schema
        schema_mapping = {
            "patient_mgmt": ["users", "facilities", "encounters"],
            "claims_proc": ["claims", "claim_activities", "collections", "health_plans"],
            "s3_landing": list(datasets.keys()),  # All tables in raw landing
        }

        conn = duckdb.connect(db_path)

        try:
            # Create schemas
            for schema in schema_mapping.keys():
                conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                print(f"  Created schema: {schema}")

            # Insert data into appropriate schemas
            for schema, tables in schema_mapping.items():
                print(f"\n  [{schema}] - {'MSSQL Patient Mgmt' if schema == 'patient_mgmt' else 'Oracle Claims Proc' if schema == 'claims_proc' else 'S3 Raw Landing'}")
                for table_name in tables:
                    if table_name in datasets:
                        df = pd.DataFrame(datasets[table_name])
                        full_table_name = f"{schema}.{table_name}"

                        # Drop existing table and create new one
                        conn.execute(f"DROP TABLE IF EXISTS {full_table_name}")
                        conn.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM df")

                        count = conn.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()[0]
                        print(f"    - {full_table_name}: {count} records")

            # Create a summary view
            conn.execute("""
                CREATE OR REPLACE VIEW main.schema_summary AS
                SELECT
                    table_schema as schema_name,
                    table_name,
                    CASE
                        WHEN table_schema = 'patient_mgmt' THEN 'MSSQL - Patient Management System'
                        WHEN table_schema = 'claims_proc' THEN 'Oracle - Claims Processing System'
                        WHEN table_schema = 's3_landing' THEN 'S3 - Raw Landing Zone'
                        ELSE 'Other'
                    END as source_system
                FROM information_schema.tables
                WHERE table_schema IN ('patient_mgmt', 'claims_proc', 's3_landing')
                ORDER BY table_schema, table_name
            """)

            print("\n  Created view: main.schema_summary")

        finally:
            conn.close()

        print(f"\nDuckDB database saved: {db_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RCM Synthetic Data Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Volume arguments
    parser.add_argument("--patients", type=int, default=100, help="Number of patients")
    parser.add_argument("--doctors", type=int, default=20, help="Number of doctors")
    parser.add_argument("--staff", type=int, default=15, help="Number of staff")
    parser.add_argument("--facilities", type=int, default=10, help="Number of facilities")
    parser.add_argument("--encounters", type=int, default=200, help="Number of encounters")
    parser.add_argument("--claims", type=int, default=300, help="Number of claims")
    parser.add_argument("--activities-per-claim", type=int, default=3, help="Avg activities per claim")

    # Date range
    parser.add_argument("--start-date", type=str, default=None,
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None,
                        help="End date (YYYY-MM-DD)")

    # Output arguments
    parser.add_argument("--format", type=str, default="csv",
                        choices=["csv", "parquet", "json", "duckdb"],
                        help="Output file format (duckdb creates multi-schema database)")
    parser.add_argument("--output-dir", type=str, default="./output",
                        help="Output directory for csv/parquet/json")
    parser.add_argument("--duckdb-path", type=str, default="./output/rcm.duckdb",
                        help="DuckDB database file path")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")

    args = parser.parse_args()

    # Parse dates
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    if args.end_date:
        end_date = datetime.fromisoformat(args.end_date)

    config = GeneratorConfig(
        num_patients=args.patients,
        num_doctors=args.doctors,
        num_staff=args.staff,
        num_facilities=args.facilities,
        num_encounters=args.encounters,
        num_claims=args.claims,
        avg_activities_per_claim=args.activities_per_claim,
        start_date=start_date,
        end_date=end_date,
        output_format=args.format,
        output_dir=args.output_dir,
        duckdb_path=args.duckdb_path,
        seed=args.seed,
    )

    generator = HealthcareDataGenerator(config)
    results = generator.generate_all()

    print("\nSummary:")
    for name, count in results.items():
        print(f"  {name}: {count} records")


if __name__ == "__main__":
    main()
