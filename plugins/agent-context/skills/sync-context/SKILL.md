---
name: sync-context
description: Sync only .agent-context/ files affected by project changes.
---

# Sync Project Context

Use after structural, dependency, command, config, convention, validation, decision, lesson, or task-state changes; also on explicit sync requests.

## Instructions

1. Detect changes with the lightest reliable source.
2. Update only owning `.agent-context/` files.
3. Merge manual additions. Do not overwrite or duplicate them.
4. Compact noisy history.
5. Report each updated file with a one-line summary.

## Change Detection

- Git: use `git diff --name-only HEAD`, `git status --porcelain`, or recent `.agent-context/` history.
- Verify optional history refs before use.
- No git: compare key files and `.agent-context/` timestamps; ask if unclear.

## File Routing

- `HANDOFF.md`: current task, next action, touched files, latest validation, blockers; clear stale task state.
- `ARCHITECTURE.md`: map, stack, entry points, boundaries, data flow, terms; on structural change, update the module map and its `last verified` date so it never misleads routing.
- `COMMANDS.md`: commands, scripts, validation profile, slow/flaky notes; latest results stay in `HANDOFF.md`.
- `CONFIG.md`: env names, secret locations, services, setup paths; never values.
- `CONVENTIONS.md`: durable style, workflow, communication, review, boundary preferences.
- `PROGRESS.md`: focus, recent done, in progress, backlog, blockers, freshness; compact old work.
- `MEMORY.md`: decisions, lessons, failed assumptions, open questions, bug roots, reusable fixes; preferences go in `CONVENTIONS.md`.
