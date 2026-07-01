#!/bin/bash
# stop hook — gently remind the agent to refresh HANDOFF.md when it looks stale.
# Fail open: never block completion if detection fails.

set -euo pipefail

input=$(cat)

python3 - "$input" <<'PY'
import json
import os
import pathlib
import subprocess
import sys


def emit(payload):
    print(json.dumps(payload))


try:
    raw = sys.argv[1]
    data = json.loads(raw) if raw else {}
except Exception:
    data = {}

if data.get("status") != "completed":
    emit({})
    raise SystemExit(0)

project_dir = os.environ.get("CURSOR_PROJECT_DIR") or ""
if not project_dir:
    for key in ("workspace_root", "project_dir", "cwd"):
        value = data.get(key)
        if isinstance(value, str) and value:
            project_dir = value
            break
if not project_dir:
    roots = data.get("workspace_roots")
    if isinstance(roots, list) and roots and isinstance(roots[0], str):
        project_dir = roots[0]
if not project_dir:
    project_dir = os.getcwd()

root = pathlib.Path(project_dir)
agent_dir = root / ".agent"
handoff = agent_dir / "HANDOFF.md"

if not agent_dir.is_dir():
    emit({})
    raise SystemExit(0)

try:
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
except Exception:
    emit({})
    raise SystemExit(0)

if status.returncode != 0 or not status.stdout.strip():
    emit({})
    raise SystemExit(0)

changed_paths = []
for line in status.stdout.splitlines():
    if len(line) < 4:
        continue
    rel = line[3:].strip()
    if " -> " in rel:
        rel = rel.split(" -> ", 1)[1].strip()
    rel = rel.strip('"')
    if not rel or rel == ".agent/HANDOFF.md":
        continue
    changed_paths.append(root / rel)

if not changed_paths:
    emit({})
    raise SystemExit(0)

latest_change = 0.0
for path in changed_paths:
    try:
        latest_change = max(latest_change, path.stat().st_mtime)
    except OSError:
        continue

# Conservative large-file signal: flag touched code files that have grown past a
# line threshold, so the agent considers splitting by responsibility. Heuristic only.
CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala", ".m", ".mm",
}
LINE_THRESHOLD = 600
MAX_BYTES = 2_000_000

large_files = []
for path in changed_paths:
    if path.suffix.lower() not in CODE_EXTS:
        continue
    try:
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            continue
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            line_count = sum(1 for _ in fh)
    except OSError:
        continue
    if line_count >= LINE_THRESHOLD:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        large_files.append((str(rel), line_count))

try:
    handoff_text = handoff.read_text(encoding="utf-8", errors="replace").strip()
    handoff_mtime = handoff.stat().st_mtime
except OSError:
    handoff_text = ""
    handoff_mtime = 0.0

handoff_stale = not (handoff_text and handoff_mtime + 2 >= latest_change)

notes = []
if handoff_stale:
    notes.append(
        "Refresh `.agent/HANDOFF.md` with the latest task state, touched files, "
        "validation, and blockers. Keep it concise; if there is no active task, say so."
    )
if large_files:
    listing = "; ".join(f"{name} (~{count} lines)" for name, count in large_files[:5])
    notes.append(
        "These touched files are large: "
        f"{listing}. If any now covers multiple responsibilities, consider splitting "
        "it by responsibility into focused modules (do not over-fragment) and update "
        "the `.agent/ARCHITECTURE.md` module map."
    )

if not notes:
    emit({})
    raise SystemExit(0)

emit({"followup_message": "Before finishing: " + " ".join(notes)})
PY
