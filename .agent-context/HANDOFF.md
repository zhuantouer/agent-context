# Agent Handoff

## Current Task
Naming cleanup plus a token trim of the always-applied rule. The preceding dual-host
(Cursor + Codex) work is finished and now validated.

## Status
All done.

Rule trim: `Update Triggers` folded into the `Ownership` table and the `.agent-context/` prefix
hoisted to the section header (10 occurrences down to 3). ~790 to ~721 tokens, 9%. Four of the six
old triggers added nothing beyond their Ownership row; the `HANDOFF.md` and `PROGRESS.md` triggers
are event-based rather than fact-based and were preserved in their rows. `Safety`,
`Architecture Checkpoint`, and `Hygiene` were deliberately left uncompressed.

Project name: `agent-context` stays. Eight candidate names were checked and all are taken, most
by direct competitors, so the differentiation moved into the copy. Both manifests, both READMEs,
and the keyword arrays now lead with what the project lacks — no index, no database, no daemon,
no MCP server, Python stdlib only, one source for two hosts.

Directory: `.agent/` is now `.agent-context/`, namespaced by its owner instead of sitting one
character from the ecosystem's `.agents/`. `git mv` plus a scripted replace of `\.agent(?![-\w])`
updated 91 references across 17 files; the negative lookahead protected `.agents/` and
`plugins/agent-context`.

Dual-host: previously code-complete but unverified because the shell had stopped responding.
The shell recovered this session and every hook smoke test passes.

## Next Action
Rewrite the install sections of `README.md` and `plugins/agent-context/README.md` for both
hosts: `./scripts/install-local.sh all`, plus the Codex restart and explicit hook-trust
approval. They currently document Cursor only, which now contradicts the new dual-host
tagline above them. Verify with `node scripts/validate-template.mjs`.

## Touched Files
- `plugins/agent-context/.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json` — description,
  `shortDescription`/`longDescription`, expanded keywords
- `README.md` — new tagline, plus a Philosophy paragraph contrasting with graph/database memory tools
- `plugins/agent-context/README.md` — new tagline
- `.agent/` → `.agent-context/` via `git mv`, plus 91 reference updates across 17 files
- `plugins/agent-context/rules/agent-context-core.mdc` — merged `Update Triggers` into `Ownership`,
  hoisted the path prefix, tightened `Startup`
- `.agent-context/MEMORY.md` — naming decisions and lessons; the three entries that described the
  old directory as an open question were rewritten by hand, since the scripted replace had turned
  them into statements that were no longer true

## Validation
- `node scripts/validate-template.mjs` — passed, before and after the rename
- All three JSON files parse; `bash -n` on both `.sh` entry points is clean
- Rename verified by search: zero remaining `\.agent(?![-\w])`, zero `agent-context-context`
  double-replacements, and the four `.agents/` ecosystem paths in `validate-template.mjs` and
  `install-local.sh` untouched
- All six `COMMANDS.md` hook smoke tests pass after the rename: Cursor SessionStart emits
  `additional_context` with no protocol; Codex SessionStart emits
  `hookSpecificOutput.additionalContext` with protocol and handoff (7280 chars, under the 10000
  limit); Cursor Stop emits `followup_message` on a completed turn and `{}` on an aborted one;
  Codex Stop emits `systemMessage` (not `decision: block`) and `{}` under the loop guard
- The stop tests return `{}` whenever the handoff is genuinely fresh, so the positive path was
  confirmed separately by touching `README.md` to make the worktree newer than the handoff; both
  hosts then fired and named `.agent-context/HANDOFF.md`
- Not yet done: a real Codex install and live session

## Source Freshness
Verified against the working tree on 2026-08-03. Competitor claims come from web searches the
same day (engramx, isaacriehm/cairn, mkupermann/throughline, chiefautism/warm-start,
agentic-cortex, several memory-bank projects).

## Blockers
None. The shell that blocked the previous session works again.

## User Instructions
Reference OpenAME's packaging but stay lightweight. Judge changes by the "Expert C" lens:
minimal change, objective signals, no premature framework.

## Notes for Next Agent
The memory directory was `.agent/` until this session. Any other project on this machine that used
an earlier install still has a `.agent/` directory, and nothing in the current code looks for it —
those projects will read as un-bootstrapped and the agent will offer to regenerate context from
scratch rather than surface the existing files. Rename them by hand, or add legacy detection
(tracked in the backlog).

`.agent-context/MEMORY.md` has a duplicated `# Project Memory` heading partway down with a second
Decisions and Lessons Learned pair, apparently a merge artifact. Left alone as unrelated to the
current task; worth consolidating when someone next edits that file.

Codex event constraints worth not re-deriving: `PreCompact` ignores plain stdout and supports
only the common output fields, `SessionEnd` is explicitly advisory, so neither can make the agent
write a handoff. `Stop` is the only event that can, via `decision: block` — deliberately not used,
because the staleness signal fires on most working turns. `SessionStart` re-fires with
`source=compact` after a compaction, and the matcher covers it.

Two leftovers outside the repo from the earlier split-package attempt: `~/plugins/agent-context-codex/`
and `[plugins."agent-context-codex@personal"]` in `~/.codex/config.toml`. Harmless (Codex skips
unresolvable entries) but worth removing by hand. Also `~/.agents/skills/` holds copies of all four
skills, which will show up alongside the plugin's once it is installed.
