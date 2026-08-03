#!/usr/bin/env python3
"""Host hook payload parsing shared by the session-start and stop hooks.

Cursor and Codex both deliver one JSON object on stdin, but they disagree on
which field carries the project directory.
"""

import json
import os
import sys

# Cursor prefers the workspace root; Codex documents `cwd` as the session's
# working directory.
PROJECT_DIR_KEYS = {
    "cursor": ("workspace_root", "project_dir", "cwd"),
    "codex": ("cwd", "workspace_root", "project_dir"),
}

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
