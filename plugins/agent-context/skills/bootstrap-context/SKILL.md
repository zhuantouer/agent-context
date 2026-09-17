---
name: bootstrap-context
description: Create concise .agent-context/ project memory when missing or explicitly refreshed.
---

# Bootstrap Project Context

Use before substantive project work when `.agent-context/` is missing, or on an explicit initialize/refresh request. Skip bootstrap for a standalone question.

## Instructions

1. If context exists, preserve it; refresh when requested without re-approval. Resolve only material conflicts with the user.
2. Scan key files relevant to the task: `README`, package/config manifests, env examples, rules and host instruction files (for example `CLAUDE.md` or `AGENTS.md`). Do not create or overwrite such files to install this protocol; do not inventory the whole repository.
3. Identify the user's outcome, success signal and current subgoal from the conversation. Label inferred criteria as assumptions; ask only when a missing choice materially changes the work.
4. Create/refresh only files with useful facts. Never store secrets. Prefer file tools or portable commands.
5. Briefly report what was captured and what remains unknown; the agent maintains the files, not the user.

## Create Files

- `ARCHITECTURE.md`: overview, stack, structure, entry points, data flow, and a module map (each module's responsibility + boundary). Record `verified against: <commit or "(no git)">` plus the paths the map covers, so a later agent can tell whether those paths moved — a bare date only proves someone typed a date.
- `COMMANDS.md`: setup/dev/test/lint/type/build/deploy commands, validation profile, scripts, command notes.
- `CONFIG.md`: env names, key locations, services, local setup; no secret values.
- `CONVENTIONS.md`: style, preferences, boundaries, review habits, vocabulary, and modular-design habits (one responsibility per file, split by responsibility not length, one-way dependencies, no over-fragmentation).
- `PROGRESS.md`: use the `update-progress` state-map template for the goal, current conclusion and coarse milestones. Detailed work belongs in `worklog/YYYY-MM-DD.md`; create a log only when there is actual work to retain, not on startup or calendar rollover.
- `MEMORY.md`: decisions and lessons with corrective guidance, plus open questions that outlive any single task.

## Rules

- Use real dates.
- No file is mandatory. Create `PROGRESS.md` when there is an objective, current conclusion or meaningful work to retain; use `update-progress` to consolidate older context. Skip empty placeholders.
- Useful for future agents, not comprehensive docs.
