#!/bin/bash
# sessionStart hook — inject .agent/ context reminder into the agent session.
# Command hooks must emit JSON on stdout (see Cursor hooks docs).

set -euo pipefail

input=$(cat)

PROJECT_DIR="${CURSOR_PROJECT_DIR:-}"
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    print('')
    raise SystemExit(0)
for key in ('workspace_root', 'project_dir', 'cwd'):
    value = data.get(key)
    if isinstance(value, str) and value:
        print(value)
        raise SystemExit(0)
roots = data.get('workspace_roots')
if isinstance(roots, list) and roots and isinstance(roots[0], str):
    print(roots[0])
" 2>/dev/null || true)
fi

if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR="$(pwd)"
fi

AGENT_DIR="${PROJECT_DIR}/.agent"

if [ -d "$AGENT_DIR" ]; then
  message=$(cat <<EOF
[Agent Context] .agent/ detected at ${AGENT_DIR}. Read these files before doing work:
- .agent/PROGRESS.md (start here — current focus and blockers)
- .agent/ARCHITECTURE.md (structure and entry points)
- .agent/COMMANDS.md (build, test, lint commands)
- .agent/CONFIG.md (env var and API key locations — paths only)
- .agent/DECISIONS.md (technical decisions and lessons)
EOF
)
else
  message=$(cat <<EOF
[Agent Context] No .agent/ directory in ${PROJECT_DIR}.
Run /bootstrap-context to scan the project and generate context files.
EOF
)
fi

python3 -c 'import json, sys; print(json.dumps({"additional_context": sys.stdin.read()}))' <<<"$message"
exit 0
