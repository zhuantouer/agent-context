#!/usr/bin/env python3
"""Host conventions for the session-start hook.

Each host delivers one JSON object on stdin. Only Codex registers this hook —
Cursor and CodeBuddy load the plugin rule through `rules/` — so the hook is a
no-op for them: build_message returns "" and the script prints `{}`.
"""

import json
import sys

HOSTS = ("cursor", "codex", "codebuddy")

# Codex has no always-applied rules slot, so SessionStart injects the protocol.
# Cursor and CodeBuddy load rules/agent-context-core.mdc themselves.
INJECT_PROTOCOL_HOSTS = frozenset({"codex"})


def parse_host(argv):
    host = argv[1] if len(argv) > 1 else "cursor"
    if host not in HOSTS:
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
