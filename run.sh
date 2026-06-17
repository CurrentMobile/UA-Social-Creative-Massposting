#!/usr/bin/env bash
# Launch Claude Code with .env loaded so ${VAR} references in .mcp.json
# (e.g. ${POSTIZ_API_KEY}) resolve. Claude Code expands these from the shell
# environment, not from .env automatically.
set -euo pipefail
cd "$(dirname "$0")"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

exec claude "$@"
