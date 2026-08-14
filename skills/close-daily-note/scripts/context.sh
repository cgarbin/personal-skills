#!/usr/bin/env bash
# Resolves everything the summary steps need in one call: the project's
# daily-notes directory, the target date and its neighbors, the source note,
# and the day's commits.
#
# Values print as key=value lines. Each Bash call from the agent is a fresh
# shell, so the agent substitutes them into later calls as literals.
#
# macOS only. The date arithmetic uses BSD `date -j -v`.
#
# Usage: context.sh [yesterday|today|YYYY-MM-DD] [project-root]
# Exit:  0 ok, 1 nothing to work with, 2 repository map does not match disk

INTENT="${1:-yesterday}"
ROOT="${2:-}"

if [ -n "$ROOT" ]; then
    PROJECT_ROOT="$ROOT"
else
    dir="$PWD"
    while [ "$dir" != "/" ] && [ ! -d "$dir/_daily-notes" ]; do
        dir=$(dirname "$dir")
    done
    PROJECT_ROOT="$dir"
fi

if [ ! -d "$PROJECT_ROOT/_daily-notes" ]; then
    echo "ERROR: no _daily-notes directory at or above $PWD" >&2
    exit 1
fi

TODAY=$(date '+%Y-%m-%d')
case "$INTENT" in
    today)     TARGET="$TODAY" ;;
    yesterday) TARGET=$(date -j -v-1d '+%Y-%m-%d') ;;
    *)         TARGET="$INTENT" ;;
esac

case "$TARGET" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
    *) echo "ERROR: cannot read '$INTENT' as a date" >&2; exit 1 ;;
esac

# BSD date normalizes an impossible date instead of rejecting it, turning
# Feb 30 into Mar 2, so the shape check above has to be backed by a round trip.
if [ "$(date -j -f '%Y-%m-%d' "$TARGET" '+%Y-%m-%d' 2>/dev/null)" != "$TARGET" ]; then
    echo "ERROR: $TARGET is not a real date" >&2
    exit 1
fi

# ISO dates compare correctly as strings.
if [ "$TARGET" \> "$TODAY" ]; then
    echo "ERROR: $TARGET is in the future" >&2
    exit 1
fi

echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "DAILY_NOTES_DIR=$PROJECT_ROOT/_daily-notes"
echo "today=$TODAY"
echo "target=$TARGET"
echo "now=$(date '+%Y-%m-%d %H:%M')"
echo "next_day=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%Y-%m-%d')"
echo "next_dow=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%a')"

# -maxdepth 2 covers the top level plus any YYYY-MM/ or YYYY/ archive folder.
echo "source_note=$(find "$PROJECT_ROOT/_daily-notes" -maxdepth 2 -name "*${TARGET}*" | head -1)"

repo_map=$(find "$PROJECT_ROOT" -maxdepth 4 -name "Repository map.md" | head -1)
REPOS=()
if [ -n "$repo_map" ]; then
    parent=$(dirname "$PROJECT_ROOT")
    while IFS= read -r name; do
        if [ -d "$parent/$name/.git" ]; then
            REPOS+=("$parent/$name")
        else
            echo "MISSING: $name is in the map but is not a git repo on disk" >&2
        fi
    done < <(awk '/^## / { sub(/^## /, ""); print }' "$repo_map")
    if [ "${#REPOS[@]}" -lt 2 ]; then
        echo "ERROR: map lists ${#REPOS[@]} repos that exist, expected at least 2" >&2
        exit 2
    fi
elif [ -d "$PROJECT_ROOT/.git" ]; then
    REPOS=("$PROJECT_ROOT")
fi

echo "repo_count=${#REPOS[@]}"
for repo_path in "${REPOS[@]}"; do
    # --branches keeps work on an unmerged feature branch from being dropped.
    commits=$(git -C "$repo_path" log \
        --after="${TARGET}T00:00:00" --before="${TARGET}T23:59:59" \
        --oneline --branches)
    if [ -n "$commits" ]; then
        printf '=== %s ===\n%s\n\n' "$repo_path" "$commits"
    fi
done
