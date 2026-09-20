# Project Configuration

## Environment Variables
- `CURSOR_PROJECT_DIR` — used by hook scripts to resolve the active project path.

## API Keys
(none detected)

## External Services
- Cursor Plugins — target runtime for plugin installation and execution. No marketplace distribution: installation is `./scripts/install-local.sh` only.

## Local Setup
Local plugin testing copies `plugin` into `~/.cursor/plugins/local/` via `./scripts/install-local.sh`. Do not symlink from outside that directory because Cursor rejects external symlinks.
# Project Configuration

## Environment Variables
No required environment variables detected.

## API Keys
No API keys detected. Do not store secret values in this repository or in `.agent-context/`.

## External Services
- Cursor plugin runtime. No marketplace distribution.

## Local Setup
- Edit plugin files under `plugin/`.
- Validate with `node scripts/validate-template.mjs`.
- Install locally with `./scripts/install-local.sh`, then reload Cursor.
