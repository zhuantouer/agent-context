#!/usr/bin/env python3
"""Host hook payload parsing shared by the session-start and stop hooks.

Every host delivers one JSON object on stdin, but they disagree on which field
carries the project directory and on the stdout envelope the hook must emit.
"""

import json
import os
import sys

# Cursor prefers the workspace root; Codex and CodeBuddy document `cwd` as the
# session's working directory (Claude-style payload).
PROJECT_DIR_KEYS = {
    "cursor": ("workspace_root", "project_dir", "cwd"),
    "codex": ("cwd", "workspace_root", "project_dir"),
    "codebuddy": ("cwd", "workspace_root", "project_dir"),
}

# Codex and CodeBuddy speak the Claude-style hook envelope (PascalCase events,
# hookSpecificOutput / systemMessage). Cursor uses its own camelCase JSON.
CLAUDE_IO_HOSTS = frozenset({"codex", "codebuddy"})

# Codex has no always-applied rules slot, so SessionStart injects the protocol.
# Cursor and CodeBuddy load rules/agent-context-core.mdc themselves.
INJECT_PROTOCOL_HOSTS = frozenset({"codex"})

HOSTS = tuple(PROJECT_DIR_KEYS)


def parse_host(argv):
    host = argv[1] if len(argv) > 1 else "cursor"
    if host not in PROJECT_DIR_KEYS:
        raise SystemExit(f"unknown host: {host}")
    return host


def read_payload():
    """Read the hook payload from stdin, tolerating empty or malformed input."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    try:
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def resolve_project_dir(host, payload):
    env_dir = os.environ.get("CURSOR_PROJECT_DIR") if host == "cursor" else None
    if env_dir:
        return env_dir
    for key in PROJECT_DIR_KEYS[host]:
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    roots = payload.get("workspace_roots")
    if isinstance(roots, list) and roots and isinstance(roots[0], str):
        return roots[0]
    return os.getcwd()
