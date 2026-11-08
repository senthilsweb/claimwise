#!/usr/bin/env python3
"""Tiny Databricks helper for the Matillion track: run SQL or upload files.

Usage:
  python dbx.py sql "SHOW SCHEMAS IN claimwise"
  python dbx.py sqlfile ../sql/00_init.sql          # statements split on ';'
  python dbx.py put local.csv /Volumes/claimwise/landing/raw/claims/claims.csv

Reads DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH, DATABRICKS_CATALOG
from matillion/.env (or the environment). Uses only the REST API: no CLI needed.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

def load_env():
    p = Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def req(method, path, body=None, raw=None, ctype="application/json"):
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    r = urllib.request.Request(host + path, data=data, method=method)
    r.add_header("Authorization", "Bearer " + os.environ["DATABRICKS_TOKEN"])
    if data is not None:
        r.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(r) as resp:
            txt = resp.read().decode() or "{}"
            return json.loads(txt) if resp.headers.get("Content-Type", "").startswith("application/json") else txt
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()}")

def run_sql(stmt):
    wh = os.environ["DATABRICKS_HTTP_PATH"].rstrip("/").split("/")[-1]
    body = {"warehouse_id": wh, "statement": stmt, "wait_timeout": "50s",
            "catalog": os.environ.get("DATABRICKS_CATALOG")}
    r = req("POST", "/api/2.0/sql/statements", body)
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(2)
        r = req("GET", f"/api/2.0/sql/statements/{r['statement_id']}")
    if r["status"]["state"] != "SUCCEEDED":
        sys.exit(f"SQL failed: {r['status']}\n{stmt}")
    cols = [c["name"] for c in r.get("manifest", {}).get("schema", {}).get("columns", [])]
    rows = r.get("result", {}).get("data_array", []) or []
    return cols, rows

def main():
    load_env()
    cmd, *args = sys.argv[1:] or ["help"]
    if cmd == "sql":
        cols, rows = run_sql(args[0])
        if cols: print("\t".join(cols))
        for row in rows: print("\t".join("" if v is None else str(v) for v in row))
    elif cmd == "sqlfile":
        text = Path(args[0]).read_text()
        for stmt in [s.strip() for s in text.split(";") if s.strip() and not all(l.strip().startswith("--") or not l.strip() for l in s.splitlines())]:
            cols, rows = run_sql(stmt)
            first = next((l for l in stmt.splitlines() if l.strip() and not l.strip().startswith("--")), "")
            print(f"ok: {first[:90]}" + (f"  -> {rows[0]}" if rows else ""))
    elif cmd == "put":
        src, dest = args
        req("PUT", "/api/2.0/fs/files" + dest + "?overwrite=true", raw=Path(src).read_bytes(), ctype="application/octet-stream")
        print(f"uploaded {src} -> {dest} ({Path(src).stat().st_size} bytes)")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
