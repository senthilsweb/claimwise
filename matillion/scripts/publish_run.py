#!/usr/bin/env python3
"""Publish the pipelines of the current git branch/commit to a Matillion environment and run the daily pipeline.

Usage: python publish_run.py [versionName] [environment]
Publishes every file under pipelines/ as a multipart artifact (headers: branch, commitHash, versionName,
environmentName), then POSTs a pipeline execution for 00_claimwise_daily and polls it to completion.
"""
import json, subprocess, sys, time, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dpc_api, urllib.request, urllib.error

PROJECT_ID = "522addcc-85fa-4237-ba4d-fac5f39c7ea3"
ROOT = Path(__file__).resolve().parents[2]
PIPELINE = "pipelines/claimwise/00_claimwise_daily.orch.yaml"
version = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y.%m.%d-%H%M")
env = sys.argv[2] if len(sys.argv) > 2 else "dev"
branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, text=True).strip()
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

boundary = "----claimwise" + uuid.uuid4().hex
body = b""
files = sorted((ROOT / "pipelines").rglob("*.yaml"))
for f in files:
    rel = f.relative_to(ROOT).as_posix()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{rel}\"; filename=\"{rel}\"\r\n"
             f"Content-Type: application/x-yaml\r\n\r\n").encode() + f.read_bytes() + b"\r\n"
body += f"--{boundary}--\r\n".encode()
req = urllib.request.Request(dpc_api.BASE + f"/v1/projects/{PROJECT_ID}/artifacts", data=body, method="POST")
for k, v in {"Authorization": "Bearer " + dpc_api.token(), "Content-Type": f"multipart/form-data; boundary={boundary}",
             "versionName": version, "environmentName": env, "commitHash": commit, "branch": branch, "Accept": "application/json"}.items():
    req.add_header(k, v)
try:
    with urllib.request.urlopen(req) as r: print("publish:", r.status, r.read().decode()[:300])
except urllib.error.HTTPError as e:
    sys.exit(f"publish failed {e.code}: {e.read().decode()[:800]}")
print(f"published {len(files)} files as version {version} from {branch}@{commit[:8]} to {env}")

s, out = dpc_api.call("POST", f"/v1/projects/{PROJECT_ID}/pipeline-executions",
                      {"pipelineName": PIPELINE, "environmentName": env, "versionName": version})
print("execute:", s, out)
if s not in (200, 201, 202): sys.exit(1)
exec_id = out["pipelineExecutionId"]
while True:
    time.sleep(20)
    s, d = dpc_api.call("GET", f"/v1/projects/{PROJECT_ID}/pipeline-executions/{exec_id}")
    st = (d.get("result") or {}).get("status") if isinstance(d, dict) else d
    print(time.strftime("%H:%M:%S"), st)
    if st not in ("RUNNING", "QUEUED", "PENDING", "STARTING"): break
s, steps = dpc_api.call("GET", f"/v1/projects/{PROJECT_ID}/pipeline-executions/{exec_id}/steps")
for x in (steps.get("results", []) if isinstance(steps, dict) else []):
    r = x.get("result") or {}
    print(f"  {str(r.get('status')):8s} {x.get('name')}  {r.get('startedAt','')[11:19]} -> {r.get('finishedAt','')[11:19]}  {r.get('message') or ''}"[:160])
