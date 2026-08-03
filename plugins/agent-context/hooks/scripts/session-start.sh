#!/bin/bash
# Cursor sessionStart entry point. The implementation is shared with the Codex
# host in session-context.py; only the output shape differs.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/session-context.py" cursor
