# Project Conventions

## Coding Style
- Keep the plugin lightweight and Markdown-first.
- Prefer concise, actionable instructions over heavyweight process frameworks.
- Keep `.agent/` files short enough for fast agent recovery.
- Keep agent-facing rules and skills in concise English; put localized explanatory docs outside the execution protocol.

## User Preferences
- Optimize for smoother, more efficient, more reliable AI-assisted programming.
- Treat token savings as useful, but secondary to better agent behavior and continuity.

## Project Boundaries
- Do not reintroduce cross-model review as a core plugin capability.
- Keep secrets out of `.agent/` files; document paths and locations only.
- Treat `.agent/HANDOFF.md` as local working state by default; commit shared knowledge files intentionally.

## Review and Validation Habits
- Validate plugin structure with `node scripts/validate-template.mjs` after modifying plugin files.

## Domain Vocabulary
- "Handoff" means the active task state a new chat should resume from.
- "Validation profile" means the project-specific map of which checks to run for which changes.
- "Single-owner routing" means each durable fact has exactly one canonical `.agent/` file.
