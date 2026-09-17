---
name: sync-context
description: Syncs affected .agent-context/ files on explicit request or after material changes to structure, dependencies, commands, config, conventions, validation, decisions, lessons or task state.
---

# Sync Project Context

## Instructions

1. Detect material changes from conversation evidence and the lightest reliable source. A clean code diff does not exclude research changes to goals, decisions or evidence.
2. Route by the protocol's `Ownership` table. Read owners before editing; preserve manual additions; do not rewrite unchanged state.
3. Use `update-progress` for PROGRESS, daily evidence and legacy migration: log detail first; update the map only for changed state, milestones or relevant links. No copied daily snapshots.
4. For structural changes, update affected architecture, `verified against` (commit plus checked worktree changes, or `(no git)`) and covered paths. Claim re-verification only for checked paths.
5. Compact noisy history; briefly report material changes, not every file.

## Change Detection

- Git: when repo changes matter, use `git diff --name-only HEAD` or `git status --porcelain`. Verify optional history refs first.
- No git: compare relevant files/known context; mark uncertainty. Ask only if a missing choice affects the work.
