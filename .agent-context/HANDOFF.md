# Agent Handoff

## Current Task
Add lightweight modular-design guardrails so the plugin nudges agents toward high-cohesion, low-coupling code instead of one growing file.

## Status
Done. Three minimal changes: (1) core rule gained an "Architecture Checkpoint" (name owning module, split by responsibility not length, no over-fragmentation, one-way deps); (2) `bootstrap-context` + `sync-context` strengthen `ARCHITECTURE.md` with a module map + `last verified` date and add modular-design habits to `CONVENTIONS.md`; (3) the `stop` hook now also emits a conservative large-file signal for touched code files over 600 lines, combined with the handoff reminder.

## Next Action
Reinstall the local plugin so changes take effect: `./scripts/install-local.sh`, then Cursor "Developer: Reload Window". Decide whether to commit.

## Touched Files
- `plugins/agent-context/rules/agent-context-core.mdc` — added Architecture Checkpoint section
- `plugins/agent-context/skills/bootstrap-context/SKILL.md` — module map + modular-design habits in generated files
- `plugins/agent-context/skills/sync-context/SKILL.md` — keep module map + `last verified` fresh on structural change
- `plugins/agent-context/hooks/scripts/stop-handoff-reminder.sh` — conservative large-file signal combined with handoff reminder

## Validation
- Last run: `node scripts/validate-template.mjs` — passed; `bash -n` on both hook scripts — passed; stop hook smoke test (handoff-stale branch and large-file branch) — both emit valid JSON
- Still needed: (none)

## Source Freshness
Checked hook scripts, core rule, bootstrap/sync skills, and `.agent/` memory on branch `main` at `efad0e3`.

## Blockers
(none)

## User Instructions
Keep the plugin lightweight; improve agents' modular architecture behavior via minimal changes (Expert C approach: objective signal loop + anti-over-split guard + module-map freshness), not a heavy workflow framework.

## Notes for Next Agent
Large-file threshold is 600 lines over a code-extension allowlist, size-capped at 2MB, fails open. It only prompts consideration; it never blocks. Adjust `LINE_THRESHOLD`/`CODE_EXTS` if too noisy.
