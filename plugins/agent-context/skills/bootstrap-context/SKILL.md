---
name: bootstrap-context
description: Create concise .agent/ project memory when missing or explicitly refreshed.
---

# Bootstrap Project Context

Use when `.agent/` is missing, the user asks to initialize/refresh context, or `/bootstrap-context` runs.

## Instructions

1. If `.agent/` exists, ask whether to refresh or keep it.
2. Scan only key files: `README`, package/config manifests, env examples, Docker/Make/just files, rules, `CLAUDE.md`, `AGENTS.md`.
3. Prefer file tools, `rg`, or portable git commands; avoid broad scans and Unix-only examples.
4. Create/refresh the files below with concise facts. Never store secrets.
5. Report detected stack, generated files, review gaps, and: "From now on, I'll auto-maintain these files. You don't need to manage them manually."

## Create Files

- `HANDOFF.md`: current task, status, next action with verification, touched files, latest validation, freshness, blockers, user instructions, notes.
- `ARCHITECTURE.md`: overview, stack, structure, entry points, key modules, data flow.
- `COMMANDS.md`: setup/dev/test/lint/type/build/deploy commands, validation profile, scripts, command notes.
- `CONFIG.md`: env names, key locations, services, local setup; no secret values.
- `CONVENTIONS.md`: style, preferences, boundaries, review habits, vocabulary.
- `PROGRESS.md`: focus, completed, older milestones, in progress, backlog, blockers, freshness.
- `MEMORY.md`: decisions and lessons with corrective guidance.

## Rules

- Use real dates.
- Minimal project: still create all files with concise "(none detected)" entries.
- Useful for future agents, not comprehensive docs.
