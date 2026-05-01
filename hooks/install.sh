#!/usr/bin/env bash
# pyxel-skill Stop hook installer.
#
# Idempotent: appends an entry to ~/.claude/settings.json's hooks.Stop list
# referencing the absolute path of stop_check_bundle.py. Skips if the entry
# already exists.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_PATH="$SCRIPT_DIR/stop_check_bundle.py"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"

if [[ ! -f "$HOOK_PATH" ]]; then
    echo "ERROR: hook script not found at $HOOK_PATH" >&2
    exit 1
fi

if [[ ! -x "$HOOK_PATH" ]]; then
    chmod +x "$HOOK_PATH"
fi

# Ensure settings.json exists with at least an empty object.
mkdir -p "$(dirname "$SETTINGS")"
if [[ ! -f "$SETTINGS" ]]; then
    echo '{}' > "$SETTINGS"
fi

# Use jq for safe JSON edits. Fail gracefully if jq is missing.
if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: jq is required. Install with: brew install jq  (or apt install jq)" >&2
    exit 1
fi

# Check whether our hook is already installed.
ALREADY_INSTALLED=$(jq -r --arg path "$HOOK_PATH" \
    '(.hooks // {}) | (.Stop // []) | map(select(.command == $path)) | length' \
    "$SETTINGS")

if [[ "$ALREADY_INSTALLED" -gt 0 ]]; then
    echo "[pyxel-skill] hook already installed at: $HOOK_PATH"
    exit 0
fi

# Append the new hook entry.
TMP="$(mktemp)"
jq --arg path "$HOOK_PATH" \
    '.hooks //= {} | .hooks.Stop //= [] | .hooks.Stop += [{"command": $path}]' \
    "$SETTINGS" > "$TMP"
mv "$TMP" "$SETTINGS"

echo "[pyxel-skill] installed Stop hook: $HOOK_PATH"
echo "[pyxel-skill] to disable, edit $SETTINGS and remove the entry."
