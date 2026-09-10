# Project Conventions

## Coding Style
- Keep plugin guidance concise and operational.
- Prefer Markdown/JSON changes that preserve existing structure and tone.
- Avoid Unix-only command examples in generated guidance; prefer Cursor file tools, `rg`, or portable git commands.
- Keep agent-facing rules and skills in concise English; put localized explanatory docs outside execution protocol.

## User Preferences
- User requested adopting three Karpathy-inspired ideas: observable success signals, surgical edit guidance, and verifiable next actions without rigid Goal/Verify fields.
- User prefers reducing plugin token cost while preserving complete semantics.
- User wants a commit recommendation at each validated milestone so work stays traceable; the agent proposes and names the scope, the user authorizes.

## Project Boundaries
- `.agent-context/HANDOFF.md` is local working state by default.
- Never store secret values in `.agent-context/CONFIG.md`.
- Keep behavioral guidance lightweight; avoid turning the plugin into a heavy workflow framework.
- Do not reintroduce cross-model review as a core plugin capability.

## Review and Validation Habits
- Run `node scripts/validate-template.mjs` for plugin structure changes.
- Keep latest validation results in `.agent-context/HANDOFF.md`.
- Before recording a rule change as shipped, confirm it with `git show HEAD:<file>`; the installed copy under `~/.cursor/plugins/local/` diverges.

## Domain Vocabulary
- Handoff: current task snapshot for new chats or context compaction.
- Validation profile: reusable checks stored in `.agent-context/COMMANDS.md`.
- Surgical edits: changed lines should trace to the user request or cleanup caused by that change.
- Single-owner routing: each durable fact has one canonical `.agent-context/` file.
