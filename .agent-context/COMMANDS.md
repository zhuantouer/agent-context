# Project Commands

## Setup
- Install deps: No package manager setup detected.

## Development
- Validate plugin structure (both hosts): `node scripts/validate-template.mjs`

## Validation Profile
- Plugin rules, skills, hooks, manifests, marketplaces, or docs: `node scripts/validate-template.mjs`
- Hook script changes: the validator, plus `bash -n` on both `.sh` entry points, plus the hook smoke tests below.
- Docs-only changes: manual review; run structure validation if plugin metadata, skills, hooks, or rules changed.

## Hook Smoke Tests
Run from the repository root with `S=plugins/agent-context/hooks/scripts` and `R=$PWD`.

- Cursor session start (expect `additional_context`, no protocol):
  `echo "{\"workspace_root\":\"$R\"}" | bash $S/session-start.sh`
- Codex session start (expect `hookSpecificOutput.additionalContext` containing the protocol and the handoff, under the 10000-char limit):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/session-context.py codex`
- Cursor stop, completed turn (expect `followup_message` when the worktree is dirty and the handoff is stale):
  `echo "{\"status\":\"completed\",\"workspace_root\":\"$R\"}" | bash $S/stop-handoff-reminder.sh`
- Cursor stop, aborted turn (expect `{}`):
  `echo "{\"status\":\"aborted\",\"workspace_root\":\"$R\"}" | bash $S/stop-handoff-reminder.sh`
- Codex stop, completed turn (expect `systemMessage`, and specifically **not** `decision: block`, which would force an extra turn):
  `echo "{\"last_assistant_message\":\"done\",\"cwd\":\"$R\"}" | python3 $S/handoff-signal.py codex`
- Codex stop, loop guard (expect `{}`):
  `echo "{\"last_assistant_message\":\"done\",\"stop_hook_active\":true,\"cwd\":\"$R\"}" | python3 $S/handoff-signal.py codex`

## Verifying a Live Codex Install
The smoke tests only prove the scripts work, not that Codex runs them. To check the real install:
- Install state, the first thing to check: `codex plugin list` (CLI lives at `/Applications/ChatGPT.app/Contents/Resources/codex`). Expect `agent-context@personal  installed, enabled`. A status of `not installed` means the marketplace entry exists but Codex never snapshotted the plugin, and the desktop UI hides it — fix with `codex plugin add agent-context@personal`.
- Marketplace discovery: `codex plugin marketplace list` — `personal` with root `$HOME` must be listed.
- The bytes Codex actually runs live in `~/.codex/plugins/cache/personal/agent-context/<version>/`, not in `~/.codex/plugins/agent-context/`. Smoke-test that copy when debugging a live install.
- Plugin load errors: `sqlite3 ~/.codex/logs_2.sqlite "SELECT datetime(ts,'unixepoch','localtime'), level, substr(feedback_log_body,1,150) FROM logs WHERE target LIKE '%plugins%' AND level='WARN' ORDER BY id DESC LIMIT 10;"` — a `configured non-curated plugin no longer exists in discovered marketplaces` warning means `~/.codex/config.toml` enables a plugin name the marketplace does not declare.
- Enabled names must match: compare `rg 'agent-context' ~/.codex/config.toml` against the `name` in `~/.agents/plugins/marketplace.json`.
- In the app: the plugin appears under Plugins, and a new session flashes the `statusMessage` from `hooks/codex-hooks.json` ("Loading agent-context protocol and handoff").
- Behavioral: ask a fresh session which file owns validation commands and when `HANDOFF.md` must be rewritten. With the protocol injected it answers `COMMANDS.md` and the start/pause/block/validate/substantial-edit triggers without reading any file.

## Build & Deploy
- Build: No build step detected.
- Local install: `./scripts/install-local.sh [cursor|codex|all]` (defaults to `cursor`).

## Custom Scripts
- `./scripts/install-local.sh` — copies the plugin to `~/.cursor/plugins/local/` (Cursor) and/or `~/.codex/plugins/` plus a merged entry in `~/.agents/plugins/marketplace.json` (Codex).
- `node scripts/validate-template.mjs` — validates both hosts' manifests, marketplaces, rules, skills, hooks, and referenced assets; asserts shared content stays host-neutral and that host event names do not cross over.

## Command Notes
- Run commands from the repository root unless a command states otherwise.
- Cursor needs "Developer: Reload Window" after reinstalling; Codex needs a restart and an explicit hook-trust approval before its hooks run.
- The validator only checks structure. Behavior changes in the hook scripts need the smoke tests above.
