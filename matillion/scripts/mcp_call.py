#!/usr/bin/env python3
"""Call the Matillion MCP server (@matillion/mcp-server) over stdio from the CLI.

Usage:
  python mcp_call.py tools                      # list tool names
  python mcp_call.py call <tool> '<json args>'  # call one tool
  python mcp_call.py describe <tool>            # show a tool's input schema

Reads MATILLION_CLIENT_ID / MATILLION_CLIENT_SECRET from the repo-root .env (or env);
MATILLION_REGION defaults to "us"; write tools are enabled (READ_ONLY_TOOLS=false).
"""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_env():
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    os.environ.setdefault("MATILLION_REGION", "us")
    os.environ.setdefault("READ_ONLY_TOOLS", "false")
    os.environ.setdefault("DEBUG", "")

class Mcp:
    def __init__(self):
        self.p = subprocess.Popen(["npx", "-y", "@matillion/mcp-server"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "claimwise-cli", "version": "0.1"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def send(self, msg):
        self.p.stdin.write(json.dumps(msg) + "\n"); self.p.stdin.flush()

    def rpc(self, method, params):
        self.n += 1
        self.send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        while True:
            line = self.p.stdout.readline()
            if not line:
                sys.exit("server closed stdout:\n" + self.p.stderr.read())
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == self.n:
                if "error" in msg:
                    sys.exit("rpc error: " + json.dumps(msg["error"], indent=1))
                return msg["result"]

    def close(self):
        self.p.stdin.close(); self.p.terminate()

def main():
    load_env()
    cmd, *args = sys.argv[1:] or ["help"]
    if cmd == "help":
        print(__doc__); return
    m = Mcp()
    try:
        if cmd == "tools":
            tools = m.rpc("tools/list", {})["tools"]
            for t in tools: print(f"{t['name']:40s} {t.get('description','')[:90]}")
        elif cmd == "describe":
            tools = m.rpc("tools/list", {})["tools"]
            t = next(t for t in tools if t["name"] == args[0])
            print(json.dumps(t, indent=1))
        elif cmd == "call":
            res = m.rpc("tools/call", {"name": args[0], "arguments": json.loads(args[1]) if len(args) > 1 else {}})
            for c in res.get("content", []):
                txt = c.get("text", json.dumps(c))
                try: print(json.dumps(json.loads(txt), indent=1))
                except Exception: print(txt)
            if res.get("isError"): sys.exit(1)
    finally:
        m.close()

if __name__ == "__main__":
    main()
