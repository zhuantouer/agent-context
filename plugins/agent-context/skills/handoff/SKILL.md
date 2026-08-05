---
name: handoff
description: Rewrite .agent-context/HANDOFF.md as the current task snapshot before pause, compaction, blockers, validation, or handoff.
---

# Handoff

Use before pauses, new chats, likely compaction, blockers, direction changes, substantive edits, validation, or explicit handoff requests.

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

## Touched Files
- `[path]` — [why it matters]

## Validation
- Last run: `[command]` — [result]
- Still needed: [checks, or "(none)"]

## Source Freshness
[Source/context checked, or "(not checked)"]

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
