"""Deploy the Claimwise Revenue Pulse AI/BI dashboard.

Reads claimwise-revenue-pulse.lvdash.json, substitutes the target catalog,
then creates-or-updates (by display name) and publishes the dashboard.

Env (loaded by `make dashboard` from dbt-pipeline/.env):
  DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH, DATABRICKS_CATALOG
"""

import json
import os
import pathlib
import sys

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import Dashboard

DISPLAY_NAME = "Claimwise Revenue Pulse"


def main() -> None:
    host = os.environ["DATABRICKS_HOST"]
    catalog = os.environ.get("DATABRICKS_CATALOG", "workspace")
    warehouse_id = os.environ["DATABRICKS_HTTP_PATH"].rstrip("/").rsplit("/", 1)[-1]

    source = pathlib.Path(__file__).parent / "claimwise-revenue-pulse.lvdash.json"
    serialized = source.read_text().replace("__CATALOG__", catalog)
    json.loads(serialized)  # fail fast on malformed JSON

    w = WorkspaceClient(host=f"https://{host}", token=os.environ["DATABRICKS_TOKEN"])

    existing = next(
        (d for d in w.lakeview.list() if d.display_name == DISPLAY_NAME), None
    )

    # Debug helper: DASHBOARD_ACTION=fetch prints the stored definition
    # (as normalized by Databricks) instead of deploying.
    if os.environ.get("DASHBOARD_ACTION") == "fetch":
        if not existing:
            sys.exit("dashboard not found")
        stored = w.lakeview.get(existing.dashboard_id)
        print(json.dumps(json.loads(stored.serialized_dashboard), indent=1))
        return
    if existing:
        dash = w.lakeview.update(
            existing.dashboard_id,
            dashboard=Dashboard(
                display_name=DISPLAY_NAME,
                serialized_dashboard=serialized,
                warehouse_id=warehouse_id,
            ),
        )
        action = "updated"
    else:
        me = w.current_user.me().user_name
        dash = w.lakeview.create(
            dashboard=Dashboard(
                display_name=DISPLAY_NAME,
                parent_path=f"/Workspace/Users/{me}",
                serialized_dashboard=serialized,
                warehouse_id=warehouse_id,
            )
        )
        action = "created"

    w.lakeview.publish(
        dash.dashboard_id, embed_credentials=True, warehouse_id=warehouse_id
    )
    print(f"{action}: {DISPLAY_NAME}")
    print(f"draft:     https://{host}/dashboardsv3/{dash.dashboard_id}")
    print(f"published: https://{host}/dashboardsv3/{dash.dashboard_id}/published")


if __name__ == "__main__":
    sys.exit(main())
