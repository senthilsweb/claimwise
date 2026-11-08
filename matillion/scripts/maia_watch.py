#!/usr/bin/env python3
"""Watch a Maia task compactly; auto-approve safe tool permissions (CONVERSATION scope), stop on questions or terminal state.
Usage: python maia_watch.py <taskId> [max_polls]
Auto-approved tools: anything except delete/destructive names. Prints chat text and tool titles.
"""
import json, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def mcp(tool, args):
    r = subprocess.run([sys.executable, str(HERE / "mcp_call.py"), "call", tool, json.dumps(args)], capture_output=True, text=True)
    m = re.search(r'\{.*\}', r.stdout, re.S)
    return json.loads(m.group(0)) if m else {"raw": r.stdout + r.stderr}
task, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 12
seen = set(); attempt = 1
for i in range(n):
    d = mcp("wait-for-agent-task", {"taskId": task, "timeoutSeconds": 45, "attempt": attempt})
    if "raw" in d: print(d["raw"][:2000]); break
    for m in d.get("messages", {}).get("results", []):
        x = m["data"]; key = x.get("messageId") or (x.get("id"), x.get("state"), x.get("title"))
        if key in seen: continue
        seen.add(key)
        if x.get("type") == "message" and not str(x.get("messageId","")).endswith("_thinking"):
            print("-", x["chatResponse"][:1500].replace("\n", "\n  "))
        elif x.get("type") == "toolStatus" and x.get("state") in ("SUCCESS", "FAILURE", "ERROR"):
            print(f"  [{x.get('state').lower()}] {x.get('title')}")
    st = d.get("stopReason"); status = d.get("task", {}).get("status")
    pend = d.get("task", {}).get("pendingDecisions", [])
    if pend:
        decisions = []
        for p in pend:
            if p["type"] == "tool" and not re.search(r"delete|drop|remove", p.get("toolName", ""), re.I):
                print(f"  >> approving {p['toolName']}: {(p.get('permissionMessage') or {}).get('title')}")
                decisions.append({"id": p["toolId"], "type": "tool", "approved": True, "scope": "CONVERSATION"})
            else:
                print("  !! NEEDS HUMAN:", json.dumps(p, indent=1)[:3000]); sys.exit(2)
        mcp("submit-agent-task-decisions", {"taskId": task, "decisions": decisions}); attempt = 1; continue
    if st in ("completed", "stopped", "errored") or status in ("COMPLETED", "STOPPED", "ERRORED", "FAILED"):
        print("TERMINAL:", st, status); sys.exit(0)
    attempt = min(attempt + 1, 10)
print("still running after", n, "polls")
