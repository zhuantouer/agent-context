#!/usr/bin/env python3
"""Stop-hook signals, shared by the Cursor and Codex hosts.

Usage: handoff-signal.py <cursor|codex>

Emits two independent signals: the handoff looks older than the work it should
describe, and a touched code file has grown large enough to be worth splitting.
They are computed separately so either can be tuned without disturbing the other.

Fails open: any detection error emits a no-op so a completed turn is never
blocked.
"""

import json
import pathlib
import subprocess
import sys

# Hosts invoke this by absolute path, so make the sibling module importable
# regardless of the working directory Python was started in.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from hook_payload import parse_host, read_payload, resolve_project_dir  # noqa: E402

# Conservative large-file signal: flag touched code files past a line threshold,
# so the agent considers splitting by responsibility. Heuristic only.
CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala", ".m", ".mm",
}
LINE_THRESHOLD = 600
MAX_BYTES = 2_000_000
GIT_TIMEOUT_SECONDS = 5


def emit(payload):
    print(json.dumps(payload))


def should_skip_turn(host, payload):
    """Only nudge after a turn that actually completed, and never twice in a row."""
    if host == "codex":
        # Codex has no status field; an assistant message means the turn produced
        # output. stop_hook_active means some Stop hook already continued this turn,
        # so stay quiet rather than repeat the warning on the continuation.
        if not payload.get("last_assistant_message"):
            return True
        return bool(payload.get("stop_hook_active"))
    return payload.get("status") != "completed"


def changed_paths(root):
    """Return worktree paths reported by git status, excluding the handoff itself."""
    try:
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except Exception:
        return None

    if status.returncode != 0 or not status.stdout.strip():
        return []

    paths = []
    for line in status.stdout.splitlines():
        if len(line) < 4:
            continue
        rel = line[3:].strip()
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1].strip()
        rel = rel.strip('"')
        if not rel or rel == ".agent-context/HANDOFF.md":
            continue
        paths.append(root / rel)
    return paths


def latest_mtime(paths):
    latest = 0.0
    for path in paths:
        try:
            latest = max(latest, path.stat().st_mtime)
        except OSError:
            continue
    return latest


def large_code_files(root, paths):
    found = []
    for path in paths:
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
            found.append((str(rel), line_count))
    return found


def handoff_is_stale(handoff, latest_change):
    try:
        text = handoff.read_text(encoding="utf-8", errors="replace").strip()
        mtime = handoff.stat().st_mtime
    except OSError:
        return True
    return not (text and mtime + 2 >= latest_change)


def handoff_note(root, paths):
    """High-frequency signal: the handoff is older than the work it should describe."""
    if not handoff_is_stale(root / ".agent-context" / "HANDOFF.md", latest_mtime(paths)):
        return None
    return (
        "Refresh `.agent-context/HANDOFF.md` with the latest task state, touched files, "
        "validation, and blockers. Keep it concise; if there is no active task, say so."
    )


def large_file_note(root, paths):
    """Low-frequency signal: a touched code file is large enough to reconsider."""
    large_files = large_code_files(root, paths)
    if not large_files:
        return None
    listing = "; ".join(f"{name} (~{count} lines)" for name, count in large_files[:5])
    return (
        "These touched files are large: "
        f"{listing}. If any now covers multiple responsibilities, consider splitting "
        "it by responsibility into focused modules (do not over-fragment) and update "
        "the `.agent-context/ARCHITECTURE.md` module map."
    )


def build_notes(root, paths):
    notes = [handoff_note(root, paths), large_file_note(root, paths)]
    return [note for note in notes if note]


def emit_notes(host, notes):
    body = " ".join(notes)
    if host == "codex":
        # Codex `Stop` could force a continuation turn via `decision: block`, but the
        # handoff signal fires on most working turns, so that would roughly double the
        # turn count. `systemMessage` surfaces the same signal in the UI at no token
        # cost and leaves the write itself to the protocol's update triggers.
        emit({"systemMessage": f"agent-context — before finishing: {body}"})
    else:
        emit({"followup_message": f"Before finishing: {body}"})


def main():
    host = parse_host(sys.argv)
    try:
        return run(host)
    except Exception:
        # Fail open: an unhandled detection error must never turn into a blocked
        # or spuriously continued turn.
        emit({})
        return 0


def run(host):
    payload = read_payload()

    if should_skip_turn(host, payload):
        emit({})
        return 0

    root = pathlib.Path(resolve_project_dir(host, payload))
    if not (root / ".agent-context").is_dir():
        emit({})
        return 0

    paths = changed_paths(root)
    if not paths:
        emit({})
        return 0

    notes = build_notes(root, paths)
    if not notes:
        emit({})
        return 0

    emit_notes(host, notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
