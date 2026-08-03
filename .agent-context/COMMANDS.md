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
