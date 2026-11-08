#!/usr/bin/env python3
"""Drive a Maia data-engineer task for the claimwise project through the MCP server.

  python maia_task.py brief                 # print the assembled brief (what Maia receives)
  python maia_task.py create [PLAN|ACT]     # create the task from the brief
  python maia_task.py wait <taskId> [n]     # poll up to 45s per call, n attempts (default 1)
  python maia_task.py msg <taskId> "text" [PLAN|ACT]
  python maia_task.py decide <taskId> '<decisions json>'
  python maia_task.py show <taskId>         # full message history
"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
PROJECT_ID = "522addcc-85fa-4237-ba4d-fac5f39c7ea3"; ENV = "dev"
SOURCE_BRANCH = "feature/claimwise-matillion"; TARGET_BRANCH = "maia/claimwise-change"

def mcp(tool, args):
    out = subprocess.run([sys.executable, str(HERE / "mcp_call.py"), "call", tool, json.dumps(args)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(out.stdout + out.stderr)
    return out.stdout

def brief():
    """The build brief sent to Maia when the project was ported from dbt (kept verbatim as a record)."""
    return (ROOT / "matillion/porting/maia-brief.md").read_text()

def main():
    cmd, *a = sys.argv[1:] or ["help"]
    if cmd == "brief":
        b = brief(); print(b); print(f"\n[{len(b)} chars]", file=sys.stderr)
    elif cmd == "create":
        mode = a[0] if a else "PLAN"
        print(mcp("create-agent-task", {"message": brief(), "agentName": "data_engineer_agent", "mode": mode,
              "projectId": PROJECT_ID, "environmentName": ENV, "sourceBranchName": SOURCE_BRANCH,
              "targetBranchName": TARGET_BRANCH}))
    elif cmd == "wait":
        n = int(a[1]) if len(a) > 1 else 1
        for i in range(1, n + 1):
            out = mcp("wait-for-agent-task", {"taskId": a[0], "timeoutSeconds": 45, "attempt": min(i, 10)})
            print(out)
            if '"timedOut"' not in out or '"timedOut": false' in out: break
    elif cmd == "msg":
        args = {"taskId": a[0], "message": a[1], "timeoutSeconds": 45}
        if len(a) > 2: args["agentConfigOverrideMode"] = a[2]
        print(mcp("send-agent-task-message", args))
    elif cmd == "decide":
        print(mcp("submit-agent-task-decisions", {"taskId": a[0], "decisions": json.loads(a[1])}))
    elif cmd == "show":
        print(mcp("get-agent-task-messages", {"taskId": a[0]}))
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
