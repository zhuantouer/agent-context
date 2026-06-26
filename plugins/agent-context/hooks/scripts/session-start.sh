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
  HANDOFF_PATH="${AGENT_DIR}/HANDOFF.md"
  if [ -s "$HANDOFF_PATH" ]; then
    handoff=$(python3 - "$HANDOFF_PATH" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8", errors="replace").strip()
max_chars = 4000
if len(text) > max_chars:
    text = text[:max_chars].rstrip() + "\n\n[truncated — read .agent/HANDOFF.md for the full handoff]"
print(text)
PY
)
    message=$(cat <<EOF
[Agent Context] .agent/ detected at ${AGENT_DIR}. Minimal handoff from .agent/HANDOFF.md:

${handoff}

Resume from the handoff first. Read .agent/PROGRESS.md for project-level status if needed; load other .agent files on demand.
EOF
)
  else
    message=$(cat <<EOF
[Agent Context] .agent/ detected at ${AGENT_DIR}, but .agent/HANDOFF.md is missing or empty.
Read .agent/PROGRESS.md before doing work. Create or refresh .agent/HANDOFF.md when starting a meaningful task. Load other .agent files on demand.
EOF
)
  fi
else
  message=$(cat <<EOF
[Agent Context] No .agent/ directory in ${PROJECT_DIR}.
Run /bootstrap-context to scan the project and generate context files.
EOF
)
fi

python3 -c 'import json, sys; print(json.dumps({"additional_context": sys.stdin.read()}))' <<<"$message"
exit 0
