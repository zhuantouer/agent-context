#!/usr/bin/env python3
"""Session-start context injection, shared by the Cursor and Codex hosts.

Usage: session-context.py <cursor|codex>

Reads the host's session-start payload on stdin and prints one JSON object on
stdout. Cursor already injects the operating protocol through its always-applied
rule, so only the Codex host prepends the protocol here.
"""

import json
import pathlib
import sys

# Hosts invoke this by absolute path, so make the sibling module importable
# regardless of the working directory Python was started in.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from hook_payload import parse_host, read_payload, resolve_project_dir  # noqa: E402

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL_PATH = PLUGIN_ROOT / "rules" / "agent-context-core.mdc"
HANDOFF_MAX_CHARS = 4000


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


def read_handoff(handoff_path):
    text = handoff_path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) > HANDOFF_MAX_CHARS:
        text = text[:HANDOFF_MAX_CHARS].rstrip()
        text += "\n\n[truncated — read .agent-context/HANDOFF.md for the full handoff]"
    return text


def build_handoff_section(project_dir):
    agent_dir = pathlib.Path(project_dir) / ".agent-context"
    if not agent_dir.is_dir():
        return (
            f"[Agent Context] No .agent-context/ directory in {project_dir}.\n"
            "Run the bootstrap-context skill to scan the project and generate context files."
        )

    handoff_path = agent_dir / "HANDOFF.md"
    try:
        has_handoff = handoff_path.stat().st_size > 0
    except OSError:
        has_handoff = False

    if not has_handoff:
        return (
            f"[Agent Context] .agent-context/ detected at {agent_dir}, but .agent-context/HANDOFF.md is missing or empty.\n"
            "Read .agent-context/PROGRESS.md before doing work. Create or refresh .agent-context/HANDOFF.md when "
            "starting a meaningful task. Load other .agent-context files on demand."
        )

    return (
        f"[Agent Context] .agent-context/ detected at {agent_dir}. Minimal handoff from .agent-context/HANDOFF.md:\n\n"
        f"{read_handoff(handoff_path)}\n\n"
        "Resume from the handoff first. Read .agent-context/PROGRESS.md for project-level status if needed; "
        "load other .agent-context files on demand."
    )


def build_message(host, project_dir):
    sections = []
    if host == "codex":
        protocol = read_protocol()
        if protocol:
            sections.append(
                "[Agent Context] Operating protocol for this session:\n\n" + protocol
            )
    sections.append(build_handoff_section(project_dir))
    return "\n\n---\n\n".join(sections)


def emit(host, message):
    if host == "codex":
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            }
        }
    else:
        payload = {"additional_context": message}
    print(json.dumps(payload))


def main():
    host = parse_host(sys.argv)
    payload = read_payload()
    emit(host, build_message(host, resolve_project_dir(host, payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
