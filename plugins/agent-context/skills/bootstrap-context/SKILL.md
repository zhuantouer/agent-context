---
name: bootstrap-context
description: Initializes missing .agent-context/ memory or explicitly refreshes it.
---

# Bootstrap Project Context

Use before substantive work if `.agent-context/` is missing, or on explicit initialize/refresh requests. Skip standalone questions.

## Instructions

1. Preserve existing context; requested refresh needs no re-approval. Ask about material conflicts only.
2. Inspect task-relevant `README`, package/config manifests, env examples, rules and host instructions (e.g. `CLAUDE.md`, `AGENTS.md`), not the whole repo. Do not create/overwrite these to install the protocol.
3. Extract user outcome, success signal and current subgoal from the conversation. Mark inferred criteria as assumptions; ask only for missing choices that materially affect the work.
4. Create/refresh only useful facts; never store secrets. Prefer file tools or portable commands.
5. Briefly report captured facts and unknowns. Maintain files yourself, not through the user.

## Create Files

- `ARCHITECTURE.md`: overview, stack, structure, entry points, data flow, module responsibilities/boundaries. Record `verified against` (commit plus checked worktree changes, or `(no git)`) and covered paths, not just a date.
- `COMMANDS.md`: setup/dev/test/lint/type/build/deploy commands, validation profile, scripts, command notes.
- `CONFIG.md`: env names, key locations, services, local setup; no secret values.
- `CONVENTIONS.md`: style, preferences, boundaries, review habits, vocabulary; modular-design habits: one responsibility per file, split by responsibility not length, one-way dependencies, no over-fragmentation.
- `PROGRESS.md`: use `update-progress` for the goal/conclusion/milestone map. Put work details in `worklog/YYYY-MM-DD.md` only when worth retaining, not on startup or date changes.
- `MEMORY.md`: decisions, lessons/corrective guidance, cross-task open questions.

## Rules

- Use real dates.
- All files optional; no empty placeholders. Create `PROGRESS.md` for an objective, current conclusion or meaningful work; consolidate older context with `update-progress`.
- Serve future agents, not comprehensive documentation.
