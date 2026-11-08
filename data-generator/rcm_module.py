"""
RCM Synthetic Data Generator Module

Generates realistic healthcare revenue cycle management (RCM) data
matching the Claimwise bronze layer schema:

- users:        id, userID, userType, name, dateOfBirth, contactInfo, specialty, department, role
- facilities:   id, facilityID, name, location, contactInfo
- health_plans: id, healthPlanID, planName, payerID
- encounters:   id, encounterID, patientID, doctorID, facilityID, date, type, duration, notes
- claims:       id, claimID, patientID, payerID, status, dateCreated, dateUpdated, amount
- activities:   id, activityID, claimID, activityDate, activityType, diagnosisCode, procedureCode, notes
- collections:  id, collectionID, claimID, date, methodOfCollection, amountCollected, status
"""

import os
import random
import argparse
from datetime import datetime, date, timedelta
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
    num_payers: int = 10
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
            num_payers=config.get("num_payers", 10),
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

    Datasets match the Matillion bronze tables:
    users, facilities, health_plans, encounters, claims, activities, collections.
    """

    # Domain constants — aligned with the silver data-quality assertions
    SPECIALTIES = [
        "Cardiology", "Family Medicine", "Internal Medicine",
        "Neurology", "Orthopedics", "Pediatrics"
    ]

    STAFF_DEPARTMENTS = ["Administration", "Nursing", "Billing", "Laboratory", "Radiology"]
    STAFF_ROLES = ["Nurse", "Admin", "Billing Specialist", "Medical Assistant", "Receptionist"]

    PAYER_NAMES = [
        "Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna",
        "Humana", "Kaiser Permanente", "Anthem", "Centene", "Molina",
        "Medicare", "Medicaid"
    ]

    PLAN_TIERS = ["Platinum", "Gold", "Silver", "Bronze", "Essential"]
    PLAN_TYPES = ["HMO", "PPO", "EPO", "POS"]

    ENCOUNTER_TYPES = [
        "Initial Visit", "Follow-up", "Emergency",
        "Routine Checkup", "Specialist Consultation"
    ]

    CLAIM_STATUSES = ["Submitted", "In Review", "Approved", "Denied", "Appealed"]
    # Realistic RCM mix: most claims resolve to Approved; a meaningful slice
    # is Denied; only a small tail is still mid-cycle at any snapshot.
    CLAIM_STATUS_WEIGHTS = [0.07, 0.10, 0.65, 0.15, 0.03]
    # Claims created in this many days before end_date have not had time to
    # fully resolve yet, so they skew toward the early-cycle statuses.
    RECENT_CLAIM_WINDOW_DAYS = 45
    RECENT_CLAIM_STATUS_WEIGHTS = [0.45, 0.35, 0.10, 0.05, 0.05]

    ACTIVITY_TYPES = [
        "Submission", "Review", "Documentation Request",
        "Appeal", "Payment Processing"
    ]

    COLLECTION_METHODS = ["Cash", "Credit Card", "Bank Transfer", "Check", "Electronic Payment"]
    COLLECTION_STATUSES = ["Processed", "Pending", "Completed", "Failed"]

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
        self.activities: List[Dict] = []
        self.collections: List[Dict] = []

        # ID tracking
        self.patient_ids: List[int] = []
        self.doctor_ids: List[int] = []
        self.payer_ids: List[int] = []
        self._used_business_ids: set = set()

    def _business_id(self, prefix: str) -> str:
        """Generate a unique business identifier like CLM47870268."""
        while True:
            candidate = f"{prefix}{random.randint(100000, 99999999)}"
            if candidate not in self._used_business_ids:
                self._used_business_ids.add(candidate)
                return candidate

    def _random_date(self, start: datetime = None, end: datetime = None) -> date:
        """Generate random date within range (never in the future)."""
        start = start or self.config.start_date
        end = end or self.config.end_date
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        if isinstance(start, datetime):
            start = start.date()
        if isinstance(end, datetime):
            end = end.date()
        end = min(end, date.today())
        delta = end - start
        random_days = random.randint(0, max(0, delta.days))
        return start + timedelta(days=random_days)

    def generate_users(self) -> List[Dict]:
        """Generate users: doctors, staff, payers, and patients."""
        self.users = []
        user_id = 1

        def base_user(user_type: str, prefix: str) -> Dict:
            return {
                "id": user_id,
                "userID": self._business_id(prefix),
                "userType": user_type,
                "name": self.fake.name(),
                "dateOfBirth": None,
                "contactInfo": self.fake.phone_number(),
                "specialty": None,
                "department": None,
                "role": None,
            }

        for _ in range(self.config.num_doctors):
            user = base_user("DOCTOR", "DR")
            user["specialty"] = random.choice(self.SPECIALTIES)
            user["dateOfBirth"] = self.fake.date_of_birth(minimum_age=30, maximum_age=70).isoformat()
            self.users.append(user)
            self.doctor_ids.append(user_id)
            user_id += 1

        for _ in range(self.config.num_staff):
            user = base_user("STAFF", "STF")
            user["department"] = random.choice(self.STAFF_DEPARTMENTS)
            user["role"] = random.choice(self.STAFF_ROLES)
            user["dateOfBirth"] = self.fake.date_of_birth(minimum_age=20, maximum_age=65).isoformat()
            self.users.append(user)
            user_id += 1

        for i in range(self.config.num_payers):
            user = base_user("PAYER", "PAY")
            user["name"] = self.PAYER_NAMES[i % len(self.PAYER_NAMES)]
            self.users.append(user)
            self.payer_ids.append(user_id)
            user_id += 1

        for _ in range(self.config.num_patients):
            user = base_user("PATIENT", "PT")
            user["dateOfBirth"] = self.fake.date_of_birth(minimum_age=1, maximum_age=90).isoformat()
            self.users.append(user)
            self.patient_ids.append(user_id)
            user_id += 1

        return self.users

    def generate_facilities(self) -> List[Dict]:
        """Generate healthcare facilities."""
        self.facilities = []
        suffixes = ["Clinic", "Hospital", "Medical Center", "Urgent Care", "Specialty Center"]

        for i in range(1, self.config.num_facilities + 1):
            facility = {
                "id": i,
                "facilityID": self._business_id("FAC"),
                "name": f"{self.fake.company()} {random.choice(suffixes)}",
                "location": f"{self.fake.street_address()}, {self.fake.city()}",
                "contactInfo": self.fake.phone_number(),
            }
            self.facilities.append(facility)

        return self.facilities

    def generate_health_plans(self) -> List[Dict]:
        """Generate health insurance plans offered by payers."""
        if not self.payer_ids:
            raise ValueError("Must generate users before health plans")

        self.health_plans = []
        plan_id = 1

        for payer_id in self.payer_ids:
            for _ in range(random.randint(1, 3)):
                plan = {
                    "id": plan_id,
                    "healthPlanID": self._business_id("HP"),
                    "planName": f"{random.choice(self.PLAN_TIERS)} {random.choice(self.PLAN_TYPES)}",
                    "payerID": payer_id,
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
            encounter = {
                "id": i,
                "encounterID": self._business_id("ENC"),
                "patientID": random.choice(self.patient_ids),
                "doctorID": random.choice(self.doctor_ids),
                "facilityID": random.choice([f["id"] for f in self.facilities]),
                "date": self._random_date().isoformat(),
                "type": random.choice(self.ENCOUNTER_TYPES),
                "duration": random.randint(10, 120),
                "notes": self.fake.paragraph(nb_sentences=3),
            }
            self.encounters.append(encounter)

        return self.encounters

    def generate_claims(self) -> List[Dict]:
        """Generate claims referencing patients and payers."""
        if not self.patient_ids or not self.payer_ids:
            raise ValueError("Must generate users before claims")

        self.claims = []
        config_end = self.config.end_date
        config_end = config_end.date() if isinstance(config_end, datetime) else config_end
        recency_cutoff = config_end - timedelta(days=self.RECENT_CLAIM_WINDOW_DAYS)

        for i in range(1, self.config.num_claims + 1):
            date_created = self._random_date()
            date_updated = self._random_date(
                start=datetime.combine(date_created, datetime.min.time())
            )

            # Recently created claims have not had time to fully resolve;
            # older claims follow the overall resolved-claim mix.
            weights = (
                self.RECENT_CLAIM_STATUS_WEIGHTS
                if date_created > recency_cutoff
                else self.CLAIM_STATUS_WEIGHTS
            )
            status = random.choices(self.CLAIM_STATUSES, weights=weights, k=1)[0]

            claim = {
                "id": i,
                "claimID": self._business_id("CLM"),
                "patientID": random.choice(self.patient_ids),
                "payerID": random.choice(self.payer_ids),
                "status": status,
                "dateCreated": date_created.isoformat(),
                "dateUpdated": date_updated.isoformat(),
                "amount": round(random.uniform(50.0, 5000.0), 2),
            }
            self.claims.append(claim)

        return self.claims

    def generate_activities(self) -> List[Dict]:
        """Generate claim lifecycle activities (every claim gets at least one)."""
        if not self.claims:
            raise ValueError("Must generate claims before activities")

        self.activities = []
        activity_id = 1

        for claim in self.claims:
            created = date.fromisoformat(claim["dateCreated"])
            updated = date.fromisoformat(claim["dateUpdated"])
            num_activities = random.randint(1, self.config.avg_activities_per_claim * 2)

            for j in range(num_activities):
                # First activity is always the submission; dates stay inside
                # the claim's created/updated window.
                window = (updated - created).days
                offset = 0 if j == 0 else random.randint(0, max(0, window))
                activity_type = "Submission" if j == 0 else random.choice(self.ACTIVITY_TYPES)

                activity = {
                    "id": activity_id,
                    "activityID": self._business_id("ACT"),
                    "claimID": claim["id"],
                    "activityDate": (created + timedelta(days=offset)).isoformat(),
                    "activityType": activity_type,
                    "diagnosisCode": f"ICD-{random.randint(10000, 99999)}",
                    "procedureCode": f"CPT-{random.randint(10000, 99999)}",
                    "notes": self.fake.paragraph(nb_sentences=3),
                }
                self.activities.append(activity)
                activity_id += 1

        return self.activities

    def generate_collections(self) -> List[Dict]:
        """Generate payment collections for approved claims only."""
        if not self.claims:
            raise ValueError("Must generate claims before collections")

        self.collections = []
        collection_id = 1

        approved_claims = [c for c in self.claims if c["status"] == "Approved"]

        for claim in approved_claims:
            date_updated = date.fromisoformat(claim["dateUpdated"])
            collection_date = min(
                date_updated + timedelta(days=random.randint(0, 60)),
                date.today(),
            )

            collection = {
                "id": collection_id,
                "collectionID": self._business_id("COL"),
                "claimID": claim["id"],
                "date": collection_date.isoformat(),
                "methodOfCollection": random.choice(self.COLLECTION_METHODS),
                # Never exceeds the claim amount. Payers mostly pay in full;
                # triangular distribution puts the common case near 100% with
                # a partial-payment tail down to 40%, instead of a flat
                # uniform spread that made "Approved" claims look underpaid.
                "amountCollected": round(
                    claim["amount"] * random.triangular(0.4, 1.0, 0.95), 2
                ),
                "status": random.choice(self.COLLECTION_STATUSES),
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

        print("  - Generating activities...")
        self.generate_activities()

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
            "activities": len(self.activities),
            "collections": len(self.collections),
        }

    def _datasets(self) -> Dict[str, List[Dict]]:
        return {
            "users": self.users,
            "facilities": self.facilities,
            "health_plans": self.health_plans,
            "encounters": self.encounters,
            "claims": self.claims,
            "activities": self.activities,
            "collections": self.collections,
        }

    def _save_all(self):
        """Save all datasets to files or DuckDB."""
        os.makedirs(self.config.output_dir, exist_ok=True)

        datasets = self._datasets()
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
        - claims_proc (Oracle): claims, activities, collections, health_plans
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
            "claims_proc": ["claims", "activities", "collections", "health_plans"],
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
    parser.add_argument("--payers", type=int, default=10, help="Number of payers")
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
        num_payers=args.payers,
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
