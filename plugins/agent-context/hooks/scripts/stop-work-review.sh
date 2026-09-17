#!/bin/bash
# Cursor stop entry point. The implementation is shared with the Codex host in
# work-signal.py; only the turn gate and output shape differ.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/work-signal.py" cursor
