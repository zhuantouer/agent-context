#!/usr/bin/env python3
"""Session-start context injection, shared by every host.

Usage: session-context.py <cursor|codex|codebuddy>

Reads the host's session-start payload on stdin and prints one JSON object on
stdout. Cursor and CodeBuddy already inject the operating protocol through the
plugin's always-applied rule, so only the Codex host prepends the protocol here.
"""

import json
import pathlib
import re
import sys

# Hosts invoke this by absolute path, so make the sibling module importable
# regardless of the working directory Python was started in.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from hook_payload import (  # noqa: E402
    CLAUDE_IO_HOSTS,
    INJECT_PROTOCOL_HOSTS,
    parse_host,
    read_payload,
    resolve_project_dir,
)

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL_PATH = PLUGIN_ROOT / "rules" / "agent-context-core.mdc"

FIELD_MAX_CHARS = {
    "Objective": 400,
    "Constraints": 400,
    "Current State": 800,
    "Next Check": 400,
}
CAPSULE_ORDER = tuple(FIELD_MAX_CHARS)
HISTORY_SECTIONS = {"Milestones", "Deferred", "Work Log"}
CAPSULE_MAX_CHARS = 2200
LEGACY_HANDOFF_CAPS = {
    "Objective": 280,
    "Current Task": 240,
    "Status": 260,
    "Next Action": 400,
    "Blockers": 200,
    "User Instructions": 240,
    "Validation": 160,
    "Notes for Next Agent": 220,
}
LEGACY_PROGRESS_CAPS = {
    "Objective": 280,
    "Current Focus": 200,
    "Goal Status": 260,
    "In Progress": 240,
    "Blockers": 200,
}
LEGACY_HISTORY = {"Completed", "Older Milestones", "Backlog", "Context Freshness"}
EMPTY_FIELD_VALUES = {"none", "none.", "(none)", "(not checked)"}


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


def parse_sections(text):
    """Return section bodies and the source line of an unclosed code fence."""
    sections = {}
    heading = None
    body = []
    fence = None
    fence_line = None
    for line_number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            if heading:
                body.append(line)
            continue
        if marker:
            fence = marker[1]
            fence_line = line_number
            if heading:
                body.append(line)
            continue
        if line.startswith("## "):
            if heading:
                sections[heading] = "\n".join(body).strip()
            heading = line[3:].strip()
            body = []
        elif heading:
            body.append(line)
    if heading:
        sections[heading] = "\n".join(body).strip()
    return sections, fence_line if fence else None


def split_sections(text):
    """Map `## Heading` -> body without promoting fenced text to headings."""
    return parse_sections(text)[0]


def clip_field(name, value, limits=None):
    """An arbitrary prefix can lose a negation or condition; omit rather than alter."""
    limit = (FIELD_MAX_CHARS if limits is None else limits).get(name, 240)
    if len(value) <= limit:
        return value, False
    return "[Content omitted: section exceeds resume budget.]", True


def render_fields(fields):
    return "\n\n".join(f"## {name}\n{value}" for name, value in fields)


def is_placeholder(value):
    return not value or value.strip().lower() in EMPTY_FIELD_VALUES


def build_capsule(text, limits=None, history=None):
    """Select current sections verbatim; report omitted information without guessing."""
    limits = FIELD_MAX_CHARS if limits is None else limits
    history = HISTORY_SECTIONS if history is None else history
    sections, unclosed_fence = parse_sections(text)
    fence_note = (
        f"\n\nUnclosed code fence at source line {unclosed_fence}; later headings may be inside the code block."
        if unclosed_fence else ""
    )
    if not sections:
        if len(text) <= min(CAPSULE_MAX_CHARS, sum(limits.values())):
            return text, fence_note
        return "[Unstructured record omitted: exceeds resume budget.]", fence_note

    fields = []
    omitted = []
    for name in limits:
        value = sections.get(name, "").strip()
        if is_placeholder(value):
            continue
        excerpt, shortened = clip_field(name, value, limits)
        fields.append((name, excerpt))
        if shortened:
            omitted.append(name)
    notes = []
    if omitted:
        notes.append("Omitted source sections: " + ", ".join(omitted) + ".")
    if any(name not in limits and name not in history and not is_placeholder(value)
           for name, value in sections.items()):
        notes.append("Additional source sections are not carried here.")
    if not fields:
        notes.append("No current-state content in recognized sections.")
    return render_fields(fields), ("\n\n" + " ".join(notes) if notes else "") + fence_note


def read_record(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").rstrip()
    except OSError:
        return ""


def record_excerpt(name, text, limits=None, history=None):
    capsule, caveat = build_capsule(text, limits, history)
    return f"Source: .agent-context/{name}\n\n{capsule}{caveat}"


def build_progress_section(project_dir):
    """Prefer a unified record; legacy sources stay separate until reconciled."""
    agent_dir = pathlib.Path(project_dir) / ".agent-context"
    if not agent_dir.is_dir():
        return f"[Agent Context] No .agent-context/ directory in {project_dir}."

    progress = read_record(agent_dir / "PROGRESS.md")
    prefix = f"[Agent Context] Project memory at {agent_dir}.\n\n"
    if "Current State" in split_sections(progress):
        return prefix + record_excerpt("PROGRESS.md", progress)

    legacy = read_record(agent_dir / "HANDOFF.md")
    sources = []
    if progress:
        sources.append(record_excerpt("PROGRESS.md", progress, LEGACY_PROGRESS_CAPS, LEGACY_HISTORY))
    if legacy:
        sources.append(record_excerpt("HANDOFF.md", legacy, LEGACY_HANDOFF_CAPS, set()))
    if not sources:
        return prefix + "PROGRESS.md is missing, empty or unreadable; no legacy work state is available."
    return prefix + "Legacy records (not yet consolidated; sources may disagree):\n\n" + "\n\n---\n\n".join(sources)


def build_message(host, project_dir):
    sections = []
    if host in INJECT_PROTOCOL_HOSTS:
        protocol = read_protocol()
        if protocol:
            sections.append(
                "[Agent Context] Operating protocol for this session:\n\n" + protocol
            )
    sections.append(build_progress_section(project_dir))
    return "\n\n---\n\n".join(sections)


def emit(host, message):
    if host in CLAUDE_IO_HOSTS:
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
