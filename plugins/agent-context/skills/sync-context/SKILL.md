---
name: sync-context
description: Sync only .agent-context/ files affected by project changes.
---

# Sync Project Context

Use after structural, dependency, command, config, convention, validation, decision, lesson, or task-state changes; also on explicit sync requests.

## Instructions

1. Detect material changes using available conversation evidence and the lightest reliable source. Research can change goals, decisions or evidence without changing code; a clean git diff does not mean nothing changed.
2. Route changes using the protocol's `Ownership` table; read owners before editing, preserve manual additions, and avoid rewrites for unchanged state.
3. Use `update-progress` for the PROGRESS state map, daily evidence logs and legacy migration. Route detail to its log first; change the map only when its state, milestones or relevant links change. No copied daily snapshot.
4. On structural change, update the affected architecture map and its `verified against: <commit>` plus covered paths. Claim re-verification only for paths actually checked.
5. Compact noisy history and briefly report material changes, not a mandatory file-by-file log.

## Change Detection

- Git: use `git diff --name-only HEAD` or `git status --porcelain` when repository changes matter. Verify optional history refs before use.
- No git: compare relevant files and known context; label uncertainty, asking only if a missing choice affects the work.
