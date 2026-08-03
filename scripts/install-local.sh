#!/usr/bin/env bash
# Install agent-context locally for testing.
#
#   ./scripts/install-local.sh [cursor|codex|all]   (default: cursor)
#
# Cursor rejects symlinks whose target is outside ~/.cursor/plugins/local/
# (see Cursor Plugins log: loadUserLocalPlugin ... rejected: symlink target is outside).
# Use this script after plugin changes, then reload the host.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_SRC="${REPO_ROOT}/plugins/agent-context"
PLUGIN_NAME="agent-context"
# Personal marketplace entries are resolved relative to $HOME.
CODEX_MARKETPLACE="${HOME}/.agents/plugins/marketplace.json"
CODEX_SOURCE_PATH="./.codex/plugins/${PLUGIN_NAME}"
# Name used before the Cursor and Codex packages were merged.
LEGACY_CODEX_NAME="agent-context-codex"

copy_plugin() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$PLUGIN_SRC" "$dest"
  chmod +x "$dest"/hooks/scripts/*.sh
}

install_cursor() {
  local dest="${HOME}/.cursor/plugins/local/${PLUGIN_NAME}"
  copy_plugin "$dest"
  echo "Installed ${PLUGIN_NAME} for Cursor: ${dest}"
  echo "  Next: Developer → Reload Window"
  echo "  Verify: Settings → Plugins → Installed (Agent Context)"
}

register_codex_marketplace() {
  MARKETPLACE_PATH="$CODEX_MARKETPLACE" \
  PLUGIN_NAME="$PLUGIN_NAME" \
  SOURCE_PATH="$CODEX_SOURCE_PATH" \
  LEGACY_NAME="$LEGACY_CODEX_NAME" \
  python3 - <<'PY'
import json
import os
import pathlib

path = pathlib.Path(os.environ["MARKETPLACE_PATH"])
name = os.environ["PLUGIN_NAME"]
legacy = os.environ["LEGACY_NAME"]

data = {"name": "personal", "interface": {"displayName": "Personal"}, "plugins": []}
if path.exists():
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    except json.JSONDecodeError as error:
        raise SystemExit(f"{path} is not valid JSON, refusing to overwrite: {error}")

plugins = [
    entry
    for entry in data.get("plugins", [])
    if isinstance(entry, dict) and entry.get("name") not in (name, legacy)
]
dropped = len(data.get("plugins", [])) - len(plugins)
plugins.append(
    {
        "name": name,
        "source": {"source": "local", "path": os.environ["SOURCE_PATH"]},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }
)
data["plugins"] = plugins
data.setdefault("name", "personal")

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"  Marketplace '{data['name']}' updated: {path} ({len(plugins)} plugin(s), {dropped} replaced)")
PY
}

install_codex() {
  local dest="${HOME}/.codex/plugins/${PLUGIN_NAME}"
  copy_plugin "$dest"
  echo "Installed ${PLUGIN_NAME} for Codex: ${dest}"
  register_codex_marketplace
  echo "  Next: restart Codex, then install/enable '${PLUGIN_NAME}' from the personal marketplace"
  echo "  Codex asks you to trust plugin hooks before they run; without trust there is no protocol injection"
}

HOST="${1:-cursor}"
case "$HOST" in
  cursor)
    install_cursor
    echo
    echo "Codex not installed. Run './scripts/install-local.sh codex' or '... all' to include it."
    ;;
  codex)
    install_codex
    ;;
  all)
    install_cursor
    echo
    install_codex
    ;;
  *)
    echo "Usage: $0 [cursor|codex|all]" >&2
    exit 1
    ;;
esac
