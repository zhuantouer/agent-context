#!/usr/bin/env python3
"""Session-start context injection, shared by every host.

Usage: session-context.py <cursor|codex|codebuddy>

Reads the host's session-start payload on stdin and prints one JSON object on
stdout. Cursor and CodeBuddy already inject the operating protocol through the
plugin's always-applied rule, so only the Codex host prepends the protocol here.
"""

import json
import pathlib
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

# Session-start capsule: enough to resume without opening the file. Carrying every
# HANDOFF.md field would just reproduce the old whole-file injection, but carrying
# too few is worse — the agent reads the file anyway and pays for both. Field names
# match the file's own headings so there is no mapping to keep in sync.
CAPSULE_ORDER = (
    "Current Task",
    "Status",
    "Next Action",
    "Blockers",
    "User Instructions",
    "Validation",
    "Notes for Next Agent",
)
# Per field, because they are not equally compressible: a clipped `Next Action`
# defeats the point of the capsule, while `Validation` only needs its headline.
FIELD_MAX_CHARS = {
    "Current Task": 200,
    "Status": 260,
    "Next Action": 400,
    "Blockers": 200,
    "User Instructions": 240,
    "Validation": 160,
    "Notes for Next Agent": 220,
}
# Backstop only. The per-field caps plus heading overhead must stay under this by
# construction; scripts/test-hooks.py asserts it rather than dropping fields at
# runtime, because silently dropping a field is the failure this design replaced.
CAPSULE_MAX_CHARS = 1850
EMPTY_FIELD_VALUES = {
    "none",
    "none.",
    "(none)",
    "(not checked)",
    "no active task.",
    "no active task",
}
# Checked before English ". " so a Chinese sentence is not cut mid-clause.
SENTENCE_ENDS = ("\n", "。", "！", "？", "；", ". ", "! ", "? ", "; ")


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


def split_sections(text):
    """Map `## Heading` -> body for one markdown document."""
    sections = {}
    heading = None
    body = []
    for line in text.splitlines():
        if line.startswith("## "):
            if heading:
                sections[heading] = "\n".join(body).strip()
            heading = line[3:].strip()
            body = []
        elif heading:
            body.append(line)
    if heading:
        sections[heading] = "\n".join(body).strip()
    return sections


def last_sentence_end(head):
    """Index of the last sentence or line boundary in `head`, or -1."""
    best = -1
    for mark in SENTENCE_ENDS:
        found = head.rfind(mark)
        if found >= 0:
            best = max(best, found + len(mark) - 1)
    return best


def clip_field(name, value):
    limit = FIELD_MAX_CHARS.get(name, 240)
    if len(value) <= limit:
        return value, False
    head = value[:limit]
    # Cut on a sentence or line boundary when one is close enough, so a clipped
    # field still reads as a statement rather than a fragment.
    boundary = last_sentence_end(head)
    if boundary > limit // 2:
        head = head[: boundary + 1]
    return head.rstrip() + " …", True


def render_fields(fields):
    return "\n\n".join(f"## {name}\n{value}" for name, value in fields)


def is_placeholder(value):
    return not value or value.strip().lower() in EMPTY_FIELD_VALUES


def build_capsule(text):
    """Return (capsule, caveat): the resume fields, plus a pointer only for the
    sections the capsule does not carry at all.

    Truncation used to slice the tail off the whole file, which silently dropped
    whatever sat last. Clipping each field instead keeps every field visible, and
    a clipped field gets `…` and nothing more: asking the agent to open the file
    whenever anything was shortened pulls the whole snapshot back into context and
    cancels the saving. A section the capsule never carries is different — it is
    invisible from here, so it is the one thing worth naming.
    """
    sections = split_sections(text)
    fields = [
        (name, clip_field(name, sections[name].strip())[0])
        for name in CAPSULE_ORDER
        if not is_placeholder(sections.get(name, ""))
    ]

    # A handoff without the expected headings cannot be selected from, so fall
    # back to a head slice — the only case where reading the file is warranted.
    if not fields:
        head = text[:CAPSULE_MAX_CHARS].rstrip()
        caveat = (
            ""
            if len(text) <= CAPSULE_MAX_CHARS
            else "\n\nTruncated; read .agent-context/HANDOFF.md for the rest."
        )
        return head, caveat

    uncarried = [
        name
        for name, value in sections.items()
        if name not in CAPSULE_ORDER and not is_placeholder(value)
    ]
    caveat = (
        f"\n\nNot carried here: {', '.join(uncarried)}. "
        "Read .agent-context/HANDOFF.md only if you need them."
        if uncarried
        else ""
    )
    return render_fields(fields), caveat


def build_handoff_section(project_dir):
    """State only. The protocol owns what to do about it; restating it here would
    put a second, drifting copy of `Startup` into every session."""
    agent_dir = pathlib.Path(project_dir) / ".agent-context"
    if not agent_dir.is_dir():
        return f"[Agent Context] No .agent-context/ directory in {project_dir}."

    handoff_path = agent_dir / "HANDOFF.md"
    try:
        text = handoff_path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        text = ""

    if not text:
        return f"[Agent Context] .agent-context/ at {agent_dir}; HANDOFF.md is missing or empty."

    capsule, caveat = build_capsule(text)
    return (
        f"[Agent Context] .agent-context/ at {agent_dir}. "
        f"Session-start capsule from HANDOFF.md:\n\n{capsule}{caveat}"
    )


def build_message(host, project_dir):
    sections = []
    if host in INJECT_PROTOCOL_HOSTS:
        protocol = read_protocol()
        if protocol:
            sections.append(
                "[Agent Context] Operating protocol for this session:\n\n" + protocol
            )
    sections.append(build_handoff_section(project_dir))
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
