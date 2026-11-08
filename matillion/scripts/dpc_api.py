#!/usr/bin/env python3
"""Direct calls to the Matillion (Maia Foundation) Public API when the MCP server lacks a tool.

Usage: python dpc_api.py GET /v1/projects/<id>
       python dpc_api.py POST /v1/projects '{"name": "..."}'
Reads MATILLION_CLIENT_ID / MATILLION_CLIENT_SECRET from the repo-root .env; region us1.
"""
import json, os, sys, urllib.request, urllib.parse, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for line in (ROOT / ".env").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
BASE = os.environ.get("MATILLION_API_BASE", "https://us1.api.matillion.com/dpc")

def token():
    data = urllib.parse.urlencode({"grant_type": "client_credentials", "audience": "https://api.matillion.com",
                                   "client_id": os.environ["MATILLION_CLIENT_ID"],
                                   "client_secret": os.environ["MATILLION_CLIENT_SECRET"]}).encode()
    r = urllib.request.Request("https://id.core.matillion.com/oauth/dpc/token", data=data)
    with urllib.request.urlopen(r) as resp:
        return json.load(resp)["access_token"]

def call(method, path, body=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None, method=method)
    r.add_header("Authorization", "Bearer " + token()); r.add_header("Content-Type", "application/json"); r.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(r) as resp:
            t = resp.read().decode(); return resp.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

if __name__ == "__main__":
    m, p, *rest = sys.argv[1:]
    s, out = call(m, p, json.loads(rest[0]) if rest else None)
    print(s); print(json.dumps(out, indent=1) if not isinstance(out, str) else out)
