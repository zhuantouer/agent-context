---
name: handoff
description: Rewrite .agent/HANDOFF.md as the current task snapshot. Use before pausing, switching chats, compaction, after substantive edits or validation, or when the user asks to hand off or resume later.
---

# Handoff

## Use When

- Before ending or pausing a meaningful task
- Before a new chat or likely context compaction
- After substantive edits, validation, blockers, or direction changes
- The user asks to hand off, resume later, wrap up, or preserve state

## Instructions

1. Read `.agent/HANDOFF.md` if present, then `.agent/PROGRESS.md`. Read other `.agent/` files only if needed.
2. Rewrite `.agent/HANDOFF.md` with the current task snapshot. Do not append history.
3. Keep it concise, factual, and action-oriented. Never store secrets.
4. Report that the handoff was updated and name the next action.

## Template

```markdown
# Agent Handoff

## Current Task
[One sentence describing the active user goal, or "No active task."]

## Status
[What is done, what is in progress, and what changed most recently.]

## Next Action
[The next concrete step a new agent should take.]

## Touched Files
- `[path]` — [why it matters]

## Validation
- Last run: `[command]` — [result]
- Still needed: [checks still needed, or "(none)"]

## Source Freshness
[Relevant source/context checked for this task, or "(not checked)"]

## Blockers
[Current blocker, missing decision, failing check, or "(none)"]

## User Instructions
[Durable instructions from the user that affect this task, or "(none)"]

## Notes for Next Agent
[Short tactical notes, gotchas, assumptions, or "(none)"]
```

## Rules

- Current snapshot only; no transcript, changelog, or append-only log.
- If there is no active task, say so and clear stale task details.
- Store only the latest validation result here. Store reusable validation rules in `.agent/COMMANDS.md`.
- If validation could not run, record why and what remains.
