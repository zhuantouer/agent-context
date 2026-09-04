# Project Commands

## Setup
- Install deps: No package manager setup detected.

## Development
- Validate plugin structure (every host): `node scripts/validate-template.mjs`
- Hook behaviour tests (stdlib only, ~1s): `python3 scripts/test-hooks.py`

## Validation Profile
- Plugin rules, skills, hooks, manifests, marketplaces, or docs: `node scripts/validate-template.mjs`
- Hook script changes: the validator, plus `python3 scripts/test-hooks.py`, plus `bash -n` on both `.sh` entry points. The smoke tests below stay useful for eyeballing real output, but the test suite is what must pass.
- `handoff` skill template changes: `python3 scripts/test-hooks.py` — it asserts the template still defines every field the session-start capsule injects.
- Docs-only changes: manual review; run structure validation if plugin metadata, skills, hooks, or rules changed.

## Hook Smoke Tests
Run from the repository root with `S=plugins/agent-context/hooks/scripts` and `R=$PWD`.

- Cursor session start (expect `additional_context` with the resume capsule, no protocol; ~1350 chars on this repo's handoff, hard ceiling 1850). Note the Codex line below invokes the Python directly — `session-start.sh` hard-codes the `cursor` argument and silently ignores any argument you append:
  `echo "{\"workspace_root\":\"$R\"}" | bash $S/session-start.sh`
- Codex session start (expect `hookSpecificOutput.additionalContext` containing the protocol and the capsule, under the 10000-char limit):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/session-context.py codex`
- CodeBuddy session start (expect `hookSpecificOutput.additionalContext` with the resume capsule and **no** protocol — CodeBuddy loads `rules/` itself):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/session-context.py codebuddy`
- Cursor stop, completed turn (expect `followup_message` only when a file **outside** `.agent-context/` is dirty and the handoff is older than it; a turn that touched only `.agent-context/` must stay silent):
  `echo "{\"status\":\"completed\",\"workspace_root\":\"$R\"}" | bash $S/stop-handoff-reminder.sh`
- Cursor stop, aborted turn (expect `{}`):
  `echo "{\"status\":\"aborted\",\"workspace_root\":\"$R\"}" | bash $S/stop-handoff-reminder.sh`
- Codex stop, completed turn (expect `systemMessage`, and specifically **not** `decision: block`, which would force an extra turn):
  `echo "{\"last_assistant_message\":\"done\",\"cwd\":\"$R\"}" | python3 $S/handoff-signal.py codex`
- Codex stop, loop guard (expect `{}`):
  `echo "{\"last_assistant_message\":\"done\",\"stop_hook_active\":true,\"cwd\":\"$R\"}" | python3 $S/handoff-signal.py codex`
- CodeBuddy stop, completed turn (expect `systemMessage`, and specifically **not** `decision: block` or Cursor's `followup_message`):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/handoff-signal.py codebuddy`

## Verifying a Live Codex Install
The smoke tests only prove the scripts work, not that Codex runs them. To check the real install:
- Install state, the first thing to check: `codex plugin list` (CLI lives at `/Applications/ChatGPT.app/Contents/Resources/codex`). Expect `agent-context@personal  installed, enabled`. A status of `not installed` means the marketplace entry exists but Codex never snapshotted the plugin, and the desktop UI hides it — fix with `codex plugin add agent-context@personal`.
- Marketplace discovery: `codex plugin marketplace list` — `personal` with root `$HOME` must be listed.
- The bytes Codex actually runs live in `~/.codex/plugins/cache/personal/agent-context/<version>/`, not in `~/.codex/plugins/agent-context/`. Smoke-test that copy when debugging a live install.
- Plugin load errors: `sqlite3 ~/.codex/logs_2.sqlite "SELECT datetime(ts,'unixepoch','localtime'), level, substr(feedback_log_body,1,150) FROM logs WHERE target LIKE '%plugins%' AND level='WARN' ORDER BY id DESC LIMIT 10;"` — a `configured non-curated plugin no longer exists in discovered marketplaces` warning means `~/.codex/config.toml` enables a plugin name the marketplace does not declare.
- Enabled names must match: compare `rg 'agent-context' ~/.codex/config.toml` against the `name` in `~/.agents/plugins/marketplace.json`.
- In the app: the plugin appears under Plugins, and a new session flashes the `statusMessage` from `hooks/codex-hooks.json` ("Loading agent-context protocol and handoff").
- Behavioral: ask a fresh session which file owns validation commands and when `HANDOFF.md` must be rewritten. With the protocol injected it answers `COMMANDS.md` and "before pause/block/handoff, or when task state materially changes" without reading any file.

## Build & Deploy
- Build: No build step detected.
- Local install: `./scripts/install-local.sh [cursor|codex|codebuddy|all]` (defaults to `cursor`).

## Custom Scripts
- `./scripts/install-local.sh` — copies the plugin to `~/.cursor/plugins/local/` (Cursor), `~/.codex/plugins/` plus a merged entry in `~/.agents/plugins/marketplace.json` (Codex), and/or `~/.codebuddy/plugins/` plus `codebuddy plugin install` when the CLI is present (CodeBuddy).
- `node scripts/validate-template.mjs` — validates every host's manifests, marketplaces, rules, skills, hooks, and referenced assets; asserts shared content stays host-neutral and that host event names do not cross over.

## Command Notes
- Run commands from the repository root unless a command states otherwise.
- Cursor needs "Developer: Reload Window" after reinstalling; Codex needs a restart and an explicit hook-trust approval before its hooks run; CodeBuddy needs `/reload-plugins` (or an IDE restart).
- The validator checks structure and reports the always-applied rule's size: a review warning past 4200 chars and a stronger warning past 6000. Neither size warning fails the run; only objective structure/drift errors do. Hook behaviour is covered by `scripts/test-hooks.py`, which builds a throwaway git repo per test.
- `scripts/test-hooks.py` commits its fixture before asserting: git collapses an untracked directory into a single `?? .agent-context/` entry, which hides which file a turn actually touched.
