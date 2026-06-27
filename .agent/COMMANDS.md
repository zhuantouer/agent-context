# Project Commands

## Setup
- Install deps: No package manager setup detected.

## Development
- Validate plugin structure: `node scripts/validate-template.mjs`

## Validation Profile
- Plugin rules, skills, hooks, metadata, or docs: `node scripts/validate-template.mjs`
- Hook script changes: `node scripts/validate-template.mjs` plus `bash -n plugins/agent-context/hooks/scripts/session-start.sh` and `bash -n plugins/agent-context/hooks/scripts/stop-handoff-reminder.sh`
- Docs-only changes: manual review; run structure validation if plugin metadata, skills, hooks, or rules changed.

## Build & Deploy
- Build: No build step detected.
- Local plugin install: `./scripts/install-local.sh`

## Custom Scripts
- `./scripts/install-local.sh` — copies the plugin into `~/.cursor/plugins/local/` for local Cursor testing.
- `node scripts/validate-template.mjs` — validates plugin manifests, rules, skills, hooks, and referenced assets.

## Command Notes
- Run commands from the repository root unless a command states otherwise.
