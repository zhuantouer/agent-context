#!/bin/bash
# Compatibility entry for cached Cursor Stop commands.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/stop-work-review.sh" "$@"
