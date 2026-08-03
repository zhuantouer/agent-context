# Agent Handoff

## Current Task
Get the Codex install actually working on this machine, and close the gap in the install script
that caused it.

## Status
Done in the repo and on disk; one manual step left for the user (restart Codex, accept the
hook-trust prompt).

The plugin never appeared in the Codex UI because its status was `not installed`, and that list
renders only installed plugins. Copying the plugin to `~/.codex/plugins/agent-context` and
declaring it in `~/.agents/plugins/marketplace.json` makes it *discoverable*; `codex plugin add
agent-context@personal` is what snapshots it into
`~/.codex/plugins/cache/personal/agent-context/0.1.2/` and enables it. Codex runs that cached
copy, never the source tree. `install-local.sh codex` stopped one step short and printed the
activation as a manual instruction the UI does not actually offer.

`scripts/install-local.sh` now runs `codex plugin add` itself, resolving the CLI from `PATH` or
from `/Applications/ChatGPT.app/Contents/Resources/codex`, and degrades to a printed command when
neither exists. `plugin add` re-copies even at an unchanged version, so it runs unconditionally.

The earlier fix (deleting the dead `[plugins."agent-context-codex@personal"]` entry from
`~/.codex/config.toml`) was necessary but not sufficient, and the advice that followed it —
"enable it from the UI" — was not actionable.

## Next Action
User-side: restart Codex, confirm `Agent Context` is listed under Plugins, and accept the
hook-trust prompt. Then verify with the behavioral check in `COMMANDS.md` — ask a fresh Codex
session which file owns validation commands; with the protocol injected it answers `COMMANDS.md`
without reading anything.

Repo-side: rewrite the install sections of `README.md` and `plugins/agent-context/README.md` for
both hosts, now that the Codex path is a single command. Verify with
`node scripts/validate-template.mjs`.

## Touched Files
- `scripts/install-local.sh` — added `codex_cli()` and `activate_codex_plugin()`; `install_codex`
  now activates and prints a `codex plugin list` verification line
- `.agent-context/COMMANDS.md` — `codex plugin list` / `marketplace list` as the first live checks,
  plus a note that the executed bytes live under `~/.codex/plugins/cache/`
- `.agent-context/MEMORY.md` — two entries on the activation gap and on `plugin add` idempotence

## Validation
- `bash -n scripts/install-local.sh` clean; `./scripts/install-local.sh codex` runs end to end and
  reports `installed, enabled`
- `codex plugin list` → `agent-context@personal  installed, enabled  0.1.2`
- `codex plugin marketplace list` → `personal` rooted at `$HOME`
- SessionStart smoke test run against the *cached* copy
  (`~/.codex/plugins/cache/personal/agent-context/0.1.2/hooks/scripts/session-context.py codex`)
  emits `hookSpecificOutput.additionalContext` with the protocol and handoff
- Cache-refresh behavior confirmed by probe: appended a marker to the source README, re-ran
  `codex plugin add` at the same version, saw the marker in the cache, then removed it and
  re-ran to confirm the cache went clean again
- Not yet done: a live Codex session (needs the app restart and hook trust)

## Source Freshness
Verified against the working tree and the live Codex install on 2026-08-03.

## Blockers
None.

## User Instructions
Reference OpenAME's packaging but stay lightweight. Judge changes by the "Expert C" lens:
minimal change, objective signals, no premature framework.

## Notes for Next Agent
Debug Codex integrations through `codex plugin list` and `~/.codex/logs_2.sqlite`, not the desktop
UI. The UI hides anything that is not installed, so "my plugin is missing" is ambiguous between
undiscovered, discovered-but-uninstalled, and installed-but-broken; the CLI distinguishes all
three in one line.

The memory directory was `.agent/` until this session. Other projects on this machine that used an
earlier install still have `.agent/` directories that nothing looks for, so they read as
un-bootstrapped. Rename by hand, or add legacy detection (tracked in the backlog).

`.agent-context/MEMORY.md` has a duplicated `# Project Memory` heading partway down with a second
Decisions and Lessons Learned pair, apparently a merge artifact. Worth consolidating when someone
next edits that file.

Codex event constraints worth not re-deriving: `PreCompact` ignores plain stdout and supports only
the common output fields, `SessionEnd` is explicitly advisory, so neither can make the agent write
a handoff. `Stop` is the only event that can, via `decision: block` — deliberately not used,
because the staleness signal fires on most working turns. `SessionStart` re-fires with
`source=compact` after a compaction, and the matcher covers it.
