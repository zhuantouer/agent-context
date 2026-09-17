# Project Commands

## Setup
- Install deps: No package manager setup detected.

## Development
- Validate plugin structure (every host): `node scripts/validate-template.mjs`
- Hook and packaging tests (Python unittest; packaging cases also require Node/Bash): `python3 scripts/test-hooks.py`

## Validation Profile
- Plugin rules, skills, hooks, manifests, marketplaces, or docs: `node scripts/validate-template.mjs`
- Hook script changes: the validator, plus `python3 scripts/test-hooks.py`, plus `bash -n` on the `.sh` entries. The smoke tests below stay useful for eyeballing real output, but the test suite is what must pass.
- Release metadata/installer changes: the same suite checks version mismatches, independent marketplace metadata versions and generated-file exclusion using temporary repositories/HOME; it never installs into the user's real HOME. Also run `bash -n scripts/install-local.sh`.
- `update-progress` template changes: the suite checks map/log partition, task links, no resume writes/log reads, legacy compatibility, whole-section omission, fence diagnostics and Codex limits. After editing a real map, inspect its rendered excerpt for missing conclusions/links rather than assuming a short line count fits.
- History migration: compare every source entry and deferred detail with destination text before removing it; verify local linked files and headings, including ambiguous dates/ranges. Do not treat counts alone as content preservation.
- Goal-alignment and execution-efficiency behavior: start with `plugins/agent-context/README.md#minimal-decision-replay`; tools-disabled output is only a preflight. Full behavior acceptance still requires tool-enabled isolated tasks through actual plugin loading after authorized installation/reload. Compare spontaneous discovery, safe action, preserved results and total cost; automated checks do not prove judgment or savings.
- Docs-only changes: manual review; run structure validation if plugin metadata, skills, hooks, or rules changed.

## Hook Smoke Tests
Run from the repository root with `S=plugins/agent-context/hooks/scripts` and `R=$PWD`.

- Cursor session start (expect `additional_context` from current PROGRESS sections, no protocol; history stays on demand and over-budget sections are labelled omitted rather than truncated. Unified template fields fit a 2200-character body backstop, excluding wrappers/caveats; legacy sources have separate budgets). Note the Codex line below invokes the Python directly — `session-start.sh` hard-codes the `cursor` argument and silently ignores any argument you append:
  `echo "{\"workspace_root\":\"$R\"}" | bash $S/session-start.sh`
- Codex session start (expect `hookSpecificOutput.additionalContext` containing the protocol and the capsule, under the configured 10000 approximate-token threshold, not a character cap; current upstream estimates `ceil(UTF-8 bytes / 4)`, checked with ASCII and multibyte fixtures):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/session-context.py codex`
- CodeBuddy session start (expect `hookSpecificOutput.additionalContext` with the resume capsule and **no** protocol — CodeBuddy loads `rules/` itself):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/session-context.py codebuddy`
- Cursor Stop (expect `{}` unless a modified code file reaches 600 lines; then an advisory `followup_message`, never a request to update records):
  `echo "{\"status\":\"completed\",\"workspace_root\":\"$R\"}" | bash $S/stop-work-review.sh`
- Cursor aborted turn (expect `{}` even with a large modified file):
  `echo "{\"status\":\"aborted\",\"workspace_root\":\"$R\"}" | bash $S/stop-work-review.sh`
- Codex completed turn (same large-file condition; `systemMessage`, never `decision: block`):
  `echo "{\"last_assistant_message\":\"done\",\"cwd\":\"$R\"}" | python3 $S/work-signal.py codex`
- Codex loop guard (expect `{}`):
  `echo "{\"last_assistant_message\":\"done\",\"stop_hook_active\":true,\"cwd\":\"$R\"}" | python3 $S/work-signal.py codex`
- CodeBuddy completed turn (same large-file condition; `systemMessage`, never `decision: block`):
  `echo "{\"cwd\":\"$R\"}" | python3 $S/work-signal.py codebuddy`

## Verifying a Live Codex Install
The smoke tests only prove the scripts work, not that Codex runs them. To check the real install:
- Install state, the first thing to check: `codex plugin list` (CLI lives at `/Applications/ChatGPT.app/Contents/Resources/codex`). Expect `agent-context@personal  installed, enabled`. A status of `not installed` means the marketplace entry exists but Codex never snapshotted the plugin, and the desktop UI hides it — fix with `codex plugin add agent-context@personal`.
- Marketplace discovery: `codex plugin marketplace list` — `personal` with root `$HOME` must be listed.
- The bytes Codex actually runs live in `~/.codex/plugins/cache/personal/agent-context/<version>/`, not in `~/.codex/plugins/agent-context/`. Smoke-test that copy when debugging a live install.
- Plugin load errors: `sqlite3 ~/.codex/logs_2.sqlite "SELECT datetime(ts,'unixepoch','localtime'), level, substr(feedback_log_body,1,150) FROM logs WHERE target LIKE '%plugins%' AND level='WARN' ORDER BY id DESC LIMIT 10;"` — a `configured non-curated plugin no longer exists in discovered marketplaces` warning means `~/.codex/config.toml` enables a plugin name the marketplace does not declare.
- Enabled names must match: compare `rg 'agent-context' ~/.codex/config.toml` against the `name` in `~/.agents/plugins/marketplace.json`.
- In the app: the plugin appears under Plugins, and a new session flashes the `statusMessage` from `hooks/codex-hooks.json` ("Loading agent-context protocol and work record").
- Behavioral: ask where current conclusions and detailed history belong. Expect `PROGRESS.md` for goal/now/milestones, `worklog/YYYY-MM-DD.md` for evidence, no daily handoff or write on unchanged status. Run the linked replay, including date gaps and interleaved tasks.

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
