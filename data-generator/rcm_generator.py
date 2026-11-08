import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md(
        """
        # RCM Synthetic Data Generator

        Generate realistic healthcare revenue cycle management (RCM) data for testing, demos, and development.
        Use the controls below to configure data volumes and parameters.
        """
    )
    return


@app.cell
def __(mo):
    mo.md("## Volume Configuration")
    return


@app.cell
def __(mo):
    # Patient and Provider Controls
    num_patients = mo.ui.slider(
        start=50, stop=1000, step=50, value=100, label="Number of Patients"
    )
    num_doctors = mo.ui.slider(
        start=5, stop=100, step=5, value=20, label="Number of Doctors"
    )
    num_staff = mo.ui.slider(
        start=5, stop=50, step=5, value=15, label="Number of Staff"
    )
    num_payers = mo.ui.slider(
        start=2, stop=11, step=1, value=10, label="Number of Payers"
    )
    num_facilities = mo.ui.slider(
        start=2, stop=50, step=2, value=10, label="Number of Facilities"
    )

    mo.vstack([
        mo.hstack([num_patients, num_doctors], justify="start"),
        mo.hstack([num_staff, num_payers, num_facilities], justify="start"),
    ])
    return num_doctors, num_facilities, num_patients, num_payers, num_staff


@app.cell
def __(mo):
    # Encounter and Claims Controls
    num_encounters = mo.ui.slider(
        start=100, stop=2000, step=100, value=200, label="Number of Encounters"
    )
    num_claims = mo.ui.slider(
        start=100, stop=3000, step=100, value=300, label="Number of Claims"
    )
    avg_activities_per_claim = mo.ui.slider(
        start=1, stop=10, step=1, value=3, label="Avg Activities per Claim"
    )

    mo.vstack([
        mo.hstack([num_encounters, num_claims], justify="start"),
        mo.hstack([avg_activities_per_claim], justify="start"),
    ])
    return avg_activities_per_claim, num_claims, num_encounters


@app.cell
def __(mo):
    mo.md("## Date Range Configuration")
    return


@app.cell
def __(mo):
    from datetime import date, timedelta

    # Date range controls
    start_date = mo.ui.date(
        value=date.today() - timedelta(days=365),
        label="Start Date"
    )
    end_date = mo.ui.date(
        value=date.today(),
        label="End Date"
    )

    mo.hstack([start_date, end_date], justify="start")
    return date, end_date, start_date, timedelta


@app.cell
def __(mo):
    mo.md("## Output Configuration")
    return


@app.cell
def __(mo):
    output_format = mo.ui.dropdown(
        options=["csv", "parquet", "json"],
        value="csv",
        label="Output Format"
    )
    output_dir = mo.ui.text(
        value="./output",
        label="Output Directory"
    )

    mo.hstack([output_format, output_dir], justify="start")
    return output_dir, output_format


@app.cell
def __(mo):
    generate_button = mo.ui.run_button(label="Generate Data")
    generate_button
    return generate_button,


@app.cell
def __(
    avg_activities_per_claim,
    end_date,
    generate_button,
    mo,
    num_claims,
    num_doctors,
    num_encounters,
    num_facilities,
    num_patients,
    num_payers,
    num_staff,
    output_dir,
    output_format,
    start_date,
):
    mo.stop(not generate_button.value)

    from rcm_module import HealthcareDataGenerator

    config = {
        "num_patients": num_patients.value,
        "num_doctors": num_doctors.value,
        "num_staff": num_staff.value,
        "num_payers": num_payers.value,
        "num_facilities": num_facilities.value,
        "num_encounters": num_encounters.value,
        "num_claims": num_claims.value,
        "avg_activities_per_claim": avg_activities_per_claim.value,
        "start_date": start_date.value,
        "end_date": end_date.value,
        "output_format": output_format.value,
        "output_dir": output_dir.value,
    }

    generator = HealthcareDataGenerator(config)
    results = generator.generate_all()

    mo.md(f"""
    ## Generation Complete

    **Configuration Used:**
    - Patients: {config['num_patients']}
    - Doctors: {config['num_doctors']}
    - Staff: {config['num_staff']}
    - Facilities: {config['num_facilities']}
    - Encounters: {config['num_encounters']}
    - Claims: {config['num_claims']}
    - Date Range: {config['start_date']} to {config['end_date']}

    **Files Generated ({output_format.value}):**
    - users.{output_format.value}: {results['users']} records
    - facilities.{output_format.value}: {results['facilities']} records
    - health_plans.{output_format.value}: {results['health_plans']} records
    - encounters.{output_format.value}: {results['encounters']} records
    - claims.{output_format.value}: {results['claims']} records
    - activities.{output_format.value}: {results['activities']} records
    - collections.{output_format.value}: {results['collections']} records

    **Output Directory:** `{output_dir.value}`
    """)
    return HealthcareDataGenerator, config, generator, results


@app.cell
def __(mo):
    mo.md(
        """
        ---
        ## Data Model Overview

        The generator creates 7 interrelated datasets matching the Claimwise
        Matillion bronze tables:

        | Dataset | Description | Key Fields |
        |---------|-------------|------------|
        | **users** | Patients, doctors, staff, and payers | id, userID, userType, name, specialty |
        | **facilities** | Healthcare facilities | id, facilityID, name, location |
        | **health_plans** | Insurance plans by payer | id, healthPlanID, planName, payerID |
        | **encounters** | Patient visits | id, encounterID, patientID, doctorID, facilityID, date |
        | **claims** | Medical claims | id, claimID, patientID, payerID, status, amount |
        | **activities** | Claim lifecycle events | id, activityID, claimID, activityDate, activityType |
        | **collections** | Payment collections | id, collectionID, claimID, amountCollected |

        ### Relationships
        - Users (PATIENT/DOCTOR) + Facilities → Encounters
        - Users (PATIENT/PAYER) → Claims
        - Users (PAYER) → Health Plans
        - Claims → Activities (every claim has at least one)
        - Claims (Approved only) → Collections
        """
    )
    return


if __name__ == "__main__":
    app.run()
