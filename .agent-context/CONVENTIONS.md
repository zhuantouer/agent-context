# Project Conventions

## Coding Style
- Keep plugin guidance concise and operational.
- Prefer Markdown/JSON changes that preserve existing structure and tone.
- Avoid Unix-only command examples in generated guidance; prefer Cursor file tools, `rg`, or portable git commands.
- Keep agent-facing rules and skills in concise English; put localized explanatory docs outside execution protocol.

## User Preferences
- User wants observable success signals, surgical edits and verifiable next actions without boilerplate forms. The 2026-09-16 goal-alignment request permits a purposeful objective summary; avoid a mandatory goal tree.
- User prefers reducing total unnecessary work and token cost while preserving capability and complete semantics; do not optimize prompt length by hiding decisive context. Proactively identify and implement safe, in-scope lossless efficiency improvements before costly work or long waits, rather than requiring the user to spot waste.
- User wants a commit recommendation at each validated milestone so work stays traceable; the agent proposes and names the scope, the user authorizes.
- Evaluate the whole design, not isolated clause patches. Findings carry recommendations; when reviewers disagree, distinguish accepted points, rejected points with reasons and decisions requiring the user.

## Project Boundaries
- `PROGRESS.md` is the sole current-state map: goal, now, coarse milestones and a few relevant links. Detailed work belongs in `worklog/YYYY-MM-DD.md`. Resume by task, not yesterday's date; no empty daily files or copied handoffs.
- Never store secret values in `.agent-context/CONFIG.md`.
- Keep behavioral guidance lightweight; avoid turning the plugin into a heavy workflow framework.
- Do not reintroduce cross-model review as a core plugin capability.

## Review and Validation Habits
- Run `node scripts/validate-template.mjs` for plugin structure changes.
- Keep current validation conclusions/limitations in `PROGRESS.md`; detailed checks and results belong in dated worklog entries, linked only where useful to the current task.
- Before recording a rule change as shipped, confirm it with `git show HEAD:<file>`; the installed copy under `~/.cursor/plugins/local/` diverges.

## Domain Vocabulary
- State map: PROGRESS.md carries goal/now/milestones and relevant links. Work logs: dated evidence by task, read on demand. Recovery is a read view, not a daily handoff artifact.
- Validation profile: reusable checks stored in `.agent-context/COMMANDS.md`.
- Surgical edits: changed lines should trace to the user request or cleanup caused by that change.
- Single-owner routing: each durable fact has one canonical `.agent-context/` file.
