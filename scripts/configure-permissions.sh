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
# ---------------------------------------------------------------------------
EXTRA_ALLOW=()
while IFS= read -r perm; do
  [[ -z "$perm" ]] && continue
  found=0
  for desired in "${DESIRED_ALLOW[@]}"; do
    [[ "$perm" == "$desired" ]] && found=1 && break
  done
  [[ $found -eq 0 ]] && EXTRA_ALLOW+=("$perm")
done <<< "$CURRENT_ALLOW"

EXTRA_DENY=()
while IFS= read -r perm; do
  [[ -z "$perm" ]] && continue
  found=0
  for desired in "${DESIRED_DENY[@]}"; do
    [[ "$perm" == "$desired" ]] && found=1 && break
  done
  [[ $found -eq 0 ]] && EXTRA_DENY+=("$perm")
done <<< "$CURRENT_DENY"

# ---------------------------------------------------------------------------
# Ask about extras
# ---------------------------------------------------------------------------
CHANGED=false

if [[ ${#ADDED_ALLOW[@]} -gt 0 || ${#ADDED_DENY[@]} -gt 0 ]]; then
  CHANGED=true
fi

if [[ ${#EXTRA_ALLOW[@]} -gt 0 || ${#EXTRA_DENY[@]} -gt 0 ]]; then
  echo ""
  echo "The following permissions exist but are NOT in the desired list:"
  idx=1
  ALL_EXTRAS=()

  for perm in "${EXTRA_ALLOW[@]}"; do
    echo "  [$idx] allow: $perm"
    ALL_EXTRAS+=("allow:$perm")
    idx=$((idx + 1))
  done
  for perm in "${EXTRA_DENY[@]}"; do
    echo "  [$idx] deny:  $perm"
    ALL_EXTRAS+=("deny:$perm")
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
      # Skip non-numeric input
      if ! [[ "$i" =~ ^[0-9]+$ ]]; then
        echo "  Skipping invalid input: $i"
        continue
      fi
      if [[ $i -ge 1 ]] && [[ $i -lt $idx ]]; then
        entry="${ALL_EXTRAS[$((i-1))]}"
        list="${entry%%:*}"
        perm="${entry#*:}"
        perm_json=$(printf '%s' "$perm" | jq -R .)
        if [[ "$list" == "allow" ]]; then
          MERGED=$(echo "$MERGED" | jq --argjson p "$perm_json" '.permissions.allow -= [$p]')
        else
          MERGED=$(echo "$MERGED" | jq --argjson p "$perm_json" '.permissions.deny -= [$p]')
        fi
        CHANGED=true
        echo "  Removed $list: $perm"
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
