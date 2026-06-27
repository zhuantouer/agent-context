# Agent Handoff

## Current Task
Compress the plugin's always-on rule and skill instructions to reduce token footprint while preserving behavior.

## Status
Rule and skill text was tightened. `bootstrap-context` was reduced from a full template dump to compact file responsibilities; `handoff`, `sync-context`, `update-progress`, and the core rule now use shorter trigger/action/constraint wording. Duplicate `.agent` snapshots are being cleaned up.

## Next Action
Review the final diff and decide whether to commit; if more plugin protocol text changes, rerun `node scripts/validate-template.mjs`.

## Touched Files
- `plugins/agent-context/rules/agent-context-core.mdc` — condensed always-on protocol
- `plugins/agent-context/skills/bootstrap-context/SKILL.md` — replaced long templates with compact file responsibilities
- `plugins/agent-context/skills/handoff/SKILL.md` — shortened trigger, steps, and template placeholders
- `plugins/agent-context/skills/sync-context/SKILL.md` — shortened change detection and routing
- `plugins/agent-context/skills/update-progress/SKILL.md` — shortened rolling ledger instructions
- `.agent/HANDOFF.md` — refreshed current snapshot
- `.agent/PROGRESS.md` — updated project ledger
- `.agent/CONVENTIONS.md` — recorded concise protocol convention
- `.agent/COMMANDS.md` — removed duplicate command sections

## Validation
- Last run: `node scripts/validate-template.mjs` — passed; `git diff --check -- plugins/agent-context/rules/agent-context-core.mdc plugins/agent-context/skills/bootstrap-context/SKILL.md plugins/agent-context/skills/handoff/SKILL.md plugins/agent-context/skills/sync-context/SKILL.md plugins/agent-context/skills/update-progress/SKILL.md` — passed; ReadLints on edited rule/skill files — no errors
- Still needed: (none)

## Source Freshness
Checked edited rule/skill files, `.agent/COMMANDS.md`, `.agent/CONVENTIONS.md`, `.agent/HANDOFF.md`, and `.agent/PROGRESS.md` on branch `main` at `0b93db7`.

## Blockers
(none)

## User Instructions
Use the fewest words that preserve complete semantics for rules and skills, reducing plugin token cost.

## Notes for Next Agent
Keep protocol text concise and action-oriented. Avoid restoring full generated templates inside always-loaded or frequently invoked skill text unless necessary.
