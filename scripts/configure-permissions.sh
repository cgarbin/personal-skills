#!/usr/bin/env bash
#
# Configure Claude Code permissions.
#
# Merges desired allow/deny lists into the settings file, then shows any
# extra entries and offers to remove them.
#
# Usage:
#   ./configure-permissions.sh --global             # ~/.claude/settings.json
#   ./configure-permissions.sh --project            # .claude/settings.local.json
#   ./configure-permissions.sh --project /path/to/project

set -eo pipefail

# ---------------------------------------------------------------------------
# Desired permissions (edit these lists to change defaults)
# ---------------------------------------------------------------------------
DESIRED_ALLOW=(
  "Read"
  "Write"
  "Bash(git *)"
  "Bash(npm *)"
  "Bash(npx *)"
  "Bash(pip *)"
  "Bash(python *)"
  "Bash(ls *)"
  "Bash(mkdir *)"
  "Bash(grep *)"
  "Bash(sed *)"
  "Bash(mv *)"
  "Bash(echo *)"
  "Bash(tail *)"
  "Bash(head *)"
  "Bash(chmod *)"
  "Bash(find *)"
  "Bash(docker *)"
)

DESIRED_DENY=(
  "Bash(rm *)"
  "Bash(curl *)"
  "Read(.env)"
  "Read(secrets/**)"
)

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed." >&2
  echo "Install with: brew install jq" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
  echo "Usage: $(basename "$0") <target>"
  echo ""
  echo "Targets:"
  echo "  --global              Modify ~/.claude/settings.json"
  echo "  --project [path]      Modify <path>/.claude/settings.local.json"
  echo "                        (defaults to current directory if path omitted)"
  exit 1
}

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
if [[ $# -eq 0 ]]; then
  usage
fi

case "$1" in
  --global)
    SETTINGS_FILE="${HOME}/.claude/settings.json"
    echo "Target: global (${SETTINGS_FILE})"
    ;;
  --project)
    PROJECT_DIR="${2:-.}"
    SETTINGS_FILE="${PROJECT_DIR}/.claude/settings.local.json"
    echo "Target: project (${SETTINGS_FILE})"
    ;;
  *)
    usage
    ;;
esac

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
# Build a jq-compatible JSON array from a bash array
array_to_json() {
  local arr=("$@")
  printf '%s\n' "${arr[@]}" | jq -R . | jq -s .
}

# ---------------------------------------------------------------------------
# Read existing settings (or start with empty object)
# ---------------------------------------------------------------------------
if [[ -f "$SETTINGS_FILE" ]]; then
  EXISTING=$(cat "$SETTINGS_FILE")
  echo "Found existing settings: $SETTINGS_FILE"
else
  EXISTING='{}'
  echo "No existing settings found. Will create: $SETTINGS_FILE"
fi

# Extract current allow/deny arrays (default to empty)
CURRENT_ALLOW=$(echo "$EXISTING" | jq -r '.permissions.allow // [] | .[]')
CURRENT_DENY=$(echo "$EXISTING" | jq -r '.permissions.deny // [] | .[]')

# ---------------------------------------------------------------------------
# Merge: add desired entries that are missing
# ---------------------------------------------------------------------------
DESIRED_ALLOW_JSON=$(array_to_json "${DESIRED_ALLOW[@]}")
DESIRED_DENY_JSON=$(array_to_json "${DESIRED_DENY[@]}")

MERGED=$(echo "$EXISTING" | jq \
  --argjson desired_allow "$DESIRED_ALLOW_JSON" \
  --argjson desired_deny "$DESIRED_DENY_JSON" \
  '
  .permissions.allow = ((.permissions.allow // []) + $desired_allow | unique) |
  .permissions.deny  = ((.permissions.deny  // []) + $desired_deny  | unique)
  ')

# ---------------------------------------------------------------------------
# Report what was added
# ---------------------------------------------------------------------------
echo ""

ADDED_ALLOW=()
for perm in "${DESIRED_ALLOW[@]}"; do
  if ! echo "$CURRENT_ALLOW" | grep -qxF "$perm"; then
    ADDED_ALLOW+=("$perm")
  fi
done

ADDED_DENY=()
for perm in "${DESIRED_DENY[@]}"; do
  if ! echo "$CURRENT_DENY" | grep -qxF "$perm"; then
    ADDED_DENY+=("$perm")
  fi
done

if [[ ${#ADDED_ALLOW[@]} -gt 0 ]] || [[ ${#ADDED_DENY[@]} -gt 0 ]]; then
  echo "Added permissions:"
  for perm in "${ADDED_ALLOW[@]}"; do
    echo "  allow: $perm"
  done
  for perm in "${ADDED_DENY[@]}"; do
    echo "  deny:  $perm"
  done
else
  echo "All desired permissions already present."
fi

# ---------------------------------------------------------------------------
# Find extra entries not in the desired lists
# (use jq throughout to handle multiline permission strings correctly)
# ---------------------------------------------------------------------------
EXTRAS_JSON=$(echo "$MERGED" | jq \
  --argjson desired_allow "$DESIRED_ALLOW_JSON" \
  --argjson desired_deny "$DESIRED_DENY_JSON" \
  '{
    allow: [.permissions.allow[] | select(. as $p | $desired_allow | index($p) | not)],
    deny:  [.permissions.deny[]  | select(. as $p | $desired_deny  | index($p) | not)]
  }')

NUM_EXTRA_ALLOW=$(echo "$EXTRAS_JSON" | jq '.allow | length')
NUM_EXTRA_DENY=$(echo "$EXTRAS_JSON" | jq '.deny | length')
NUM_EXTRAS=$((NUM_EXTRA_ALLOW + NUM_EXTRA_DENY))

# ---------------------------------------------------------------------------
# Ask about extras
# ---------------------------------------------------------------------------
CHANGED=false

if [[ ${#ADDED_ALLOW[@]} -gt 0 || ${#ADDED_DENY[@]} -gt 0 ]]; then
  CHANGED=true
fi

if [[ $NUM_EXTRAS -gt 0 ]]; then
  echo ""
  echo "The following permissions exist but are NOT in the desired list:"
  idx=1

  for ((i=0; i<NUM_EXTRA_ALLOW; i++)); do
    perm=$(echo "$EXTRAS_JSON" | jq -r ".allow[$i]")
    # Show first line only for readability. Multiline entries are truncated
    first_line=$(echo "$perm" | head -1)
    if [[ $(echo "$perm" | wc -l) -gt 1 ]]; then
      echo "  [$idx] allow: ${first_line}..."
    else
      echo "  [$idx] allow: $perm"
    fi
    idx=$((idx + 1))
  done
  for ((i=0; i<NUM_EXTRA_DENY; i++)); do
    perm=$(echo "$EXTRAS_JSON" | jq -r ".deny[$i]")
    first_line=$(echo "$perm" | head -1)
    if [[ $(echo "$perm" | wc -l) -gt 1 ]]; then
      echo "  [$idx] deny:  ${first_line}..."
    else
      echo "  [$idx] deny:  $perm"
    fi
    idx=$((idx + 1))
  done

  echo ""
  echo "Enter numbers to remove (comma-separated), 'all' to remove all, or press Enter to keep:"
  read -r RESPONSE

  if [[ -n "$RESPONSE" ]]; then
    REMOVE_INDICES=()
    if [[ "$RESPONSE" == "all" ]]; then
      for ((i=1; i<idx; i++)); do
        REMOVE_INDICES+=("$i")
      done
    else
      IFS=',' read -ra REMOVE_INDICES <<< "$RESPONSE"
    fi

    for i in "${REMOVE_INDICES[@]}"; do
      i=$(echo "$i" | tr -d ' ')
      if ! [[ "$i" =~ ^[0-9]+$ ]]; then
        echo "  Skipping invalid input: $i"
        continue
      fi
      if [[ $i -ge 1 ]] && [[ $i -lt $idx ]]; then
        # Map 1-based index to the extras JSON arrays
        if [[ $i -le $NUM_EXTRA_ALLOW ]]; then
          list="allow"
          ji=$((i - 1))
          perm_json=$(echo "$EXTRAS_JSON" | jq ".allow[$ji]")
          MERGED=$(echo "$MERGED" | jq --argjson p "$perm_json" '.permissions.allow -= [$p]')
        else
          list="deny"
          ji=$((i - NUM_EXTRA_ALLOW - 1))
          perm_json=$(echo "$EXTRAS_JSON" | jq ".deny[$ji]")
          MERGED=$(echo "$MERGED" | jq --argjson p "$perm_json" '.permissions.deny -= [$p]')
        fi
        CHANGED=true
        perm_display=$(echo "$perm_json" | jq -r . | head -1)
        echo "  Removed $list: $perm_display"
      else
        echo "  Skipping out-of-range: $i"
      fi
    done
  else
    echo "  Keeping all extra permissions."
  fi
else
  echo ""
  echo "No extra permissions found outside the desired list."
fi

# ---------------------------------------------------------------------------
# Write result
# ---------------------------------------------------------------------------
if [[ "$CHANGED" == "true" ]]; then
  mkdir -p "$(dirname "$SETTINGS_FILE")"
  # Back up existing file before overwriting
  if [[ -f "$SETTINGS_FILE" ]]; then
    cp "$SETTINGS_FILE" "${SETTINGS_FILE}.bak"
  fi
  echo "$MERGED" | jq . > "$SETTINGS_FILE"
  echo ""
  echo "Updated $SETTINGS_FILE (backup: ${SETTINGS_FILE}.bak):"
  jq . "$SETTINGS_FILE"
else
  echo ""
  echo "No changes needed. $SETTINGS_FILE left unchanged."
fi
