#!/usr/bin/env python3
"""Session-start protocol delivery for hosts without an always-applied rule slot.

Usage: session-context.py <cursor|codex|codebuddy>

Reads the host's session-start payload on stdin and prints one JSON object on
stdout. Cursor and CodeBuddy load the operating protocol through the plugin's
always-applied rule and register no SessionStart hook, so only the Codex host
receives the protocol here.

The work record is never injected: the protocol tells the agent to read
`PROGRESS.md` itself, which keeps one source of truth instead of an excerpt that
can silently omit a constraint.
"""

import json
import pathlib
import sys

# Hosts invoke this by absolute path, so make the sibling module importable
# regardless of the working directory Python was started in.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from hook_payload import (  # noqa: E402
    INJECT_PROTOCOL_HOSTS,
    parse_host,
    read_payload,
)

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL_PATH = PLUGIN_ROOT / "rules" / "agentic-protocol-core.mdc"


def read_protocol():
    """Return the protocol body from the canonical rule file, without frontmatter."""
    try:
        text = PROTOCOL_PATH.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]
    return text.strip()


def build_message(host):
    """Only hosts without a rules slot need the protocol; others get nothing."""
    if host not in INJECT_PROTOCOL_HOSTS:
        return ""
    protocol = read_protocol()
    if not protocol:
        return ""
    return "[Agentic 方法论] 本会话按以下方法论工作：\n\n" + protocol


def emit(message):
    """Codex is the only host that receives anything, and it expects the Claude-style envelope."""
    if not message:
        print(json.dumps({}))
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }))


def main():
    host = parse_host(sys.argv)
    # Drain stdin: the payload is unused, but leaving it unread can block the
    # host on a full pipe.
    read_payload()
    emit(build_message(host))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
