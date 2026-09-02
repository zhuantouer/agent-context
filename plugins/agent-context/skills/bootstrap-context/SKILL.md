---
name: bootstrap-context
description: Create concise .agent-context/ project memory when missing or explicitly refreshed.
---

# Bootstrap Project Context

Use when `.agent-context/` is missing, the user asks to initialize/refresh context, or the `bootstrap-context` skill is invoked.

## Instructions

1. If `.agent-context/` exists, ask whether to refresh or keep it.
2. Scan only key files: `README`, package/config manifests, env examples, Docker/Make/just files, rules, `CLAUDE.md`, `AGENTS.md`.
3. Prefer file tools, `rg`, or portable git commands; avoid broad scans and Unix-only examples.
4. Create/refresh the files below with concise facts. Never store secrets.
5. Report detected stack, generated files, review gaps, and: "From now on, I'll auto-maintain these files. You don't need to manage them manually."

## Create Files

- `HANDOFF.md`: current task, status, next action with verification, blockers, latest validation (including what source was checked), user instructions, notes. Follow the `handoff` skill's template; the session-start hook injects these fields.
- `ARCHITECTURE.md`: overview, stack, structure, entry points, data flow, and a module map (each module's responsibility + boundary). Record `verified against: <commit or "(no git)">` plus the paths the map covers, so a later agent can tell whether those paths moved — a bare date only proves someone typed a date.
- `COMMANDS.md`: setup/dev/test/lint/type/build/deploy commands, validation profile, scripts, command notes.
- `CONFIG.md`: env names, key locations, services, local setup; no secret values.
- `CONVENTIONS.md`: style, preferences, boundaries, review habits, vocabulary, and modular-design habits (one responsibility per file, split by responsibility not length, one-way dependencies, no over-fragmentation).
- `PROGRESS.md`: focus, completed, older milestones, in progress, backlog, blockers, freshness.
- `MEMORY.md`: decisions and lessons with corrective guidance, plus open questions that outlive any single task.

## Rules

- Use real dates.
- Always create `HANDOFF.md` and `PROGRESS.md`. Create the other five only where the project has facts to record; a file of "(none detected)" entries costs every later agent a read and teaches nothing. Name the skipped ones in the report so the user knows they are available.
- Useful for future agents, not comprehensive docs.
