---
name: sync-context
description: Update only the .agent/ files affected by project changes. Use after new modules, dependency changes, refactors, new commands/config, learned conventions, or when the user asks to sync context.
---

# Sync Project Context

## Use When

- New modules, directories, dependencies, commands, config, or services
- Refactors that change structure, entry points, or data flow
- New durable conventions, preferences, validation rules, decisions, or lessons
- Task state changes that future agents need
- The user asks to sync or update context

## Instructions

1. Detect what changed with the lightest reliable source.
2. Update only the owning `.agent/` files below.
3. Merge manual additions. Do not overwrite or duplicate them.
4. Compact noisy old detail instead of accumulating logs.
5. Report each updated file with a one-line summary.

## Change Detection

- Git repo: use `git diff --name-only HEAD`, `git status --porcelain`, or recent `.agent/` history.
- If `HEAD~5` is useful, first verify it exists.
- No git: compare key config files and `.agent/` timestamps; ask the user if unclear.
- Never fail the workflow because a history command is unavailable.

## File Routing

#### HANDOFF.md
- Rewrite current task snapshot: status, next action, touched files, latest validation, blockers.
- Clear stale details if there is no active task.
- Keep it short enough for new-chat startup.

#### ARCHITECTURE.md
- Project map, tech stack, entry points, module boundaries, data flow, stable terms.

#### COMMANDS.md
- Commands, scripts, validation profile, slow/flaky notes, command-specific failure modes.
- Store latest validation results in `HANDOFF.md`, not here.

#### CONFIG.md
- Environment variables, secret locations, external services, local setup paths. Never secret values.

#### CONVENTIONS.md
- Durable coding style, workflow, naming, communication, review, and project-boundary preferences.
- User corrections that should change future behavior.

#### PROGRESS.md
- Current focus, recent completed work, in-progress work, backlog, blockers, context freshness.
- Compact old completed work into milestone summaries when noisy.

#### MEMORY.md
- Durable decisions, lessons, failed assumptions, bug roots, and reusable corrective guidance.
- Put preferences in `CONVENTIONS.md`, not here.
