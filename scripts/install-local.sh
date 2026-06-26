#!/usr/bin/env bash
# Install agent-context into ~/.cursor/plugins/local/ for local testing.
#
# Cursor rejects symlinks whose target is outside ~/.cursor/plugins/local/
# (see Cursor Plugins log: loadUserLocalPlugin ... rejected: symlink target is outside).
# Use this script after plugin changes, then Developer: Reload Window.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_SRC="${REPO_ROOT}/plugins/agent-context"
PLUGIN_DEST="${HOME}/.cursor/plugins/local/agent-context"

mkdir -p "${HOME}/.cursor/plugins/local"
rm -rf "${PLUGIN_DEST}"
cp -R "${PLUGIN_SRC}" "${PLUGIN_DEST}"
chmod +x "${PLUGIN_DEST}"/hooks/scripts/*.sh

echo "Installed agent-context to ${PLUGIN_DEST}"
echo "Next: Developer → Reload Window in Cursor"
echo "Verify: Settings → Plugins → Installed (Agent Context)"
