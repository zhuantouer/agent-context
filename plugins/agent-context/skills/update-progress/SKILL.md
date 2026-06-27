---
name: update-progress
description: Update .agent/PROGRESS.md as the rolling project ledger.
---

# Update Progress

Use when starting/finishing work, changing focus/backlog/blockers, syncing context, or answering status.

## Instructions

1. Read `.agent/PROGRESS.md`.
2. Status-only and unchanged: report; do not rewrite.
3. Otherwise rewrite using the template.
4. Keep recent detail; compact old work.
5. Refresh `HANDOFF.md` if next action, validation, touched files, or blockers changed.

## Template

```markdown
# Project Progress

## Current Focus
[One current focus]

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
- Tactical next action, touched files, latest validation -> `HANDOFF.md`.
- Do not hide blockers.
- Report focus, completed change, blockers, and next backlog item when relevant.
