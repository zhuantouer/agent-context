# Project Progress

## Current Focus
Dual-host (Cursor + Codex) packaging for the agent-context plugin.

## Completed
- [x] (2026-08-03) Trimmed the always-applied rule from ~790 to ~721 tokens by folding `Update Triggers` into the `Ownership` table and hoisting the repeated `.agent-context/` prefix out of it; behavioral sections left intact.
- [x] (2026-08-03) Renamed the memory directory `.agent/` to `.agent-context/` so it is namespaced by its owner instead of sitting one character from the ecosystem's `.agents/`; 91 references updated across 17 files.
- [x] (2026-08-03) Kept the name `agent-context` after finding all eight candidate names taken, and moved differentiation into the manifests, keywords, and README taglines: no index, no database, no daemon, no MCP server, stdlib-only hooks, one source for two hosts.
- [x] (2026-08-03) Ran all six hook smoke tests plus the validator on both hosts; every result matched `COMMANDS.md`, clearing the validation that the unresponsive shell had blocked.
- [x] (2026-08-03) Made stop signals advisory on both hosts and decoupled the stale-handoff signal from the large-file signal; Codex now emits `systemMessage` instead of forcing a continuation turn.
- [x] (2026-08-03) Merged the split Codex package into one dual-manifest package: host-neutral protocol/skills, single shared hook implementation, Codex protocol injection at SessionStart, Codex marketplace, dual-host install script, and validator drift assertions.
- [x] (2026-08-03) Reviewed OpenAME dual-host plugin packaging (`sync-codex-plugins.js`, dual manifests, separate hook JSON, Codex marketplace); refined recommended approach.
- [x] (2026-08-01) Surveyed Codex plugins/skills/hooks/AGENTS.md vs current Cursor plugin; mapped gaps and recommended dual-manifest approach.
- [x] (2026-07-01) Added modular-design guardrails: core-rule Architecture Checkpoint, module map + `last verified` in ARCHITECTURE guidance, modular habits in CONVENTIONS, and a conservative large-file signal in the stop hook.
- [x] (2026-06-27) Condensed core rule/skills; observable success signals; verifiable handoff next actions.
- [x] (2026-06-26) Project context + core plugin capabilities (memory, handoff, conventions, validation, hooks, lessons).

## Older Milestones
(none)

## In Progress
- [ ] A real Codex install and live session check (scripted smoke tests pass; the in-host path is untested)

## Backlog
- Rewrite the install sections of `README.md` and `plugins/agent-context/README.md` for both hosts; they still document Cursor only, which now contradicts the dual-host taglines above them
- Decide whether the hooks should detect a legacy `.agent/` directory left by the old naming and point the user at it, instead of silently treating the project as un-bootstrapped
- Optional: have `bootstrap-context` offer an `AGENTS.md` pointer for Codex users who do not trust plugin hooks
- Housekeeping: consolidate the duplicated `# Project Memory` heading and repeated sections in `.agent-context/MEMORY.md`

## Blockers
- None. The shell recovered and all previously blocked validation has run.

## Context Freshness
- Last sync: 2026-08-03
- Source revision: working tree on `main`, Codex packaging changes uncommitted
