---
name: update-progress
description: Update .agent/PROGRESS.md as a rolling project ledger. Use when starting or completing work, changing blockers, discovering backlog, syncing context, or answering status questions.
---

# Update Progress

## Use When

- After completing a task or milestone
- When starting a new task
- When blockers, backlog, or current focus change
- When context was just synced
- When the user asks for status

## Instructions

1. Read `.agent/PROGRESS.md`.
2. If the user only wants status and nothing changed, report only; do not rewrite.
3. Otherwise rewrite `.agent/PROGRESS.md` using the template below.
4. Keep recent detail. Compact old completed work into milestone summaries instead of growing forever.
5. Refresh `.agent/HANDOFF.md` too if the active task's next action, validation, touched files, or blockers changed.

## Template

```markdown
# Project Progress

## Current Focus
[The one thing you're working on right now]

## Completed
- [x] (YYYY-MM-DD) Task — brief description

## Older Milestones
- YYYY-MM or YYYY QN: Summary of older completed work

## In Progress
- [ ] Task — current status

## Backlog
- [ ] Task — description

## Blockers
- (none, or description)

## Context Freshness
- Last sync: YYYY-MM-DD
- Source revision: [git commit/branch if available, or "(unknown)"]
```

## Rules

- Use real dates from the system.
- Keep `Current Focus` singular.
- Keep descriptions one line.
- Put tactical next action, touched files, and latest validation in `.agent/HANDOFF.md`, not here.
- Do not hide blockers.
- Report current focus, completed change, blockers, and next backlog item when relevant.
