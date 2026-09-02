---
name: handoff
description: Rewrite .agent-context/HANDOFF.md as the current task snapshot before a pause, block, or handoff, or when task state materially changes.
---

# Handoff

The protocol's `Ownership` table owns the triggers. Beyond them, also use before a new chat or likely compaction, and on explicit request.

## Instructions

1. Read `HANDOFF.md`, `PROGRESS.md`, then only needed `.agent-context/` files.
2. Move anything that outlives this task to `PROGRESS.md` or `MEMORY.md`; the rewrite discards the rest.
3. Rewrite `.agent-context/HANDOFF.md`; never append.
4. Keep it concise, factual, secret-free, and action-oriented.
5. Make `Next Action` concrete and verifiable, preferably with a `COMMANDS.md` check.
6. Report the update and next action.

## Template

```markdown
# Agent Handoff

## Current Task
[Active goal and what "done" means, or "No active task."]

## Status
[Done / in progress / latest change.]

## Next Action
[Concrete next step + verification.]

## Validation
- Last run: `[command]` — [result]
- Still needed: [checks, or "(none)"]
- Source checked: [what was read and when, or "(not checked)"]

## Blockers
[Blocker, missing decision, failing check, or "(none)"]

## User Instructions
[Task-relevant durable instructions, or "(none)"]

## Notes for Next Agent
[Tactical notes, gotchas, assumptions, or "(none)"]
```

## Rules

- Snapshot only; no transcript or changelog.
- No active task: say so and clear stale details.
- Do not add Goal/Verify fields; encode verification in `Next Action`.
- Latest validation here; reusable checks in `COMMANDS.md`.
- If validation did not run, say why and what remains.
- Do not list touched files; `git status` and the diff already carry them.
- Every section above is injected at session start, each clipped to a few hundred characters. Front-load each one: the capsule must be enough to resume, or the next agent pays for both it and the file.
- A section you invent beyond the template is not injected; the capsule only names it. Put anything a resuming agent needs inside the template's sections.
