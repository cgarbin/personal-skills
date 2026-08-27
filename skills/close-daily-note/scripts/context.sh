#!/usr/bin/env bash
# Resolves everything the summary steps need in one call: the project's
# daily-notes directory, the target date and its neighbors, the source note,
# the day's commits, and the signal counts that decide whether the day has
# anything worth summarizing.
#
# The signal counts come from here rather than from the agent so the empty-day
# stop condition can be checked before the note is read at all.
#
# All key=value lines print first, then any `=== label ===` blocks. Each Bash
# call from the agent is a fresh shell, so the agent substitutes the values into
# later calls as literals.
#
# macOS only. The date arithmetic uses BSD `date -j -v`.
#
# Usage: context.sh [yesterday|today|YYYY-MM-DD] [project-root]
# Exit:  0 ok, 1 nothing to work with

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

# Archive layouts vary (YYYY/, YYYY-MM/, YYYY/YYYY-MM/), so the whole tree is
# searched and the shallowest hit wins. That keeps a live note at the top level
# ahead of an archived copy of the same date, which `head -1` alone would pick
# in whatever order find happened to walk.
SOURCE_NOTE=$(find "$PROJECT_ROOT/_daily-notes" -type f -name "*${TARGET}*.md" \
    | awk '{ depth = gsub("/", "/"); print depth "\t" $0 }' \
    | sort -n | head -1 | cut -f2-)

echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "DAILY_NOTES_DIR=$PROJECT_ROOT/_daily-notes"
echo "today=$TODAY"
echo "target=$TARGET"
echo "now=$(date '+%Y-%m-%d %H:%M')"
echo "next_day=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%Y-%m-%d')"
echo "next_dow=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%a')"
echo "source_note=$SOURCE_NOTE"

# --- signals ---------------------------------------------------------------
# Section boundaries are top-level headings, matched case-insensitively. The
# checked-off task lines go to a temp file so every key=value line can print
# ahead of every block.

DONE_FILE=$(mktemp "${TMPDIR:-/tmp}/close-daily-note.XXXXXX") || exit 1
trap 'rm -f "$DONE_FILE"' EXIT

if [ -n "$SOURCE_NOTE" ]; then
    awk -v donefile="$DONE_FILE" '
      # The character class rejects a lone "#" left by a stray keystroke, which
      # occurs in these notes and would otherwise end the section it sits in.
      /^# [^[:space:]]/ {
        heading = tolower($0)
        sub(/[[:space:]]+$/, "", heading)
        if (heading == "# pomodoros")               { phase = "pomodoros"; next }
        if (heading == "# next tasks")              { phase = "tasks";     next }
        if (heading == "# notes")                   { phase = "notes";     next }
        if (heading == "# generated daily summary") { phase = "summary"; has_summary = 1; next }
        phase = "other"
        next
      }
      # A pomodoro counts only once it names a task, so the empty template stub
      # left in every new note does not read as a worked day.
      phase == "pomodoros" && index($0, "🍅") {
        if (match($0, /\[task::[^]]*\]/)) {
          field = substr($0, RSTART + 7, RLENGTH - 8)
          gsub(/[[:space:]]/, "", field)
          if (field != "") pomodoros++
        }
      }
      # Both bullet styles appear in practice: "- [x]" and "1. [x]", nested or not.
      phase == "tasks" {
        if (match($0, /^[[:space:]]*([-*]|[0-9]+\.)[[:space:]]*\[[ xX]\]/)) {
          if (substr($0, RSTART, RLENGTH) ~ /\[[[:space:]]\]/) open_tasks++
          else { done_tasks++; done_lines = done_lines $0 "\n" }
        }
      }
      phase == "notes" && /[^[:space:]]/ { notes_lines++ }
      END {
        print "has_summary=" (has_summary ? "yes" : "no")
        print "pomodoros=" pomodoros + 0
        print "done_tasks=" done_tasks + 0
        print "open_tasks=" open_tasks + 0
        print "notes_lines=" notes_lines + 0
        if (done_lines != "") printf "=== done tasks ===\n%s\n", done_lines > donefile
      }
    ' "$SOURCE_NOTE"
else
    echo "has_summary=no"
    echo "pomodoros=0"
    echo "done_tasks=0"
    echo "open_tasks=0"
    echo "notes_lines=0"
fi

# --- repos -----------------------------------------------------------------
# Two independent sources, because a project is either git-backed itself, or a
# notes-only project pointing at sibling repos, or both. Neither is required:
# a plain notes vault reports repo_count=0 and the summary leans on the note.

REPOS=()

# rev-parse rather than a `.git` directory test, so linked worktrees and
# submodules (where .git is a file) resolve, and a project nested inside a repo
# resolves to that repo's root.
repo_root() {
    [ -d "$1" ] || return 1
    git -C "$1" rev-parse --show-toplevel 2>/dev/null
}

add_repo() {
    local resolved="$1" existing
    [ -n "$resolved" ] || return 0
    for existing in "${REPOS[@]}"; do
        [ "$existing" = "$resolved" ] && return 0
    done
    REPOS+=("$resolved")
}

add_repo "$(repo_root "$PROJECT_ROOT")"

# A "Repository map.md" lets a project name the repos whose commits belong in
# the summary. Its `## ` headings are directory names, resolved as siblings of
# the project root.
#
# Maps also carry prose sections, and a heading is not self-evidently a repo
# name, so unresolved headings are reported as data rather than warned about.
# Guessing produced a MISSING warning for every prose heading on every run.
MAP_HEADINGS=0
MAP_REPOS=0
MAP_UNRESOLVED=""
repo_map=$(find "$PROJECT_ROOT" -maxdepth 4 -name "Repository map.md" | head -1)
if [ -n "$repo_map" ]; then
    parent=$(dirname "$PROJECT_ROOT")
    while IFS= read -r name; do
        MAP_HEADINGS=$((MAP_HEADINGS + 1))
        resolved=$(repo_root "$parent/$name") || resolved=""
        if [ -n "$resolved" ]; then
            MAP_REPOS=$((MAP_REPOS + 1))
            add_repo "$resolved"
        else
            MAP_UNRESOLVED="${MAP_UNRESOLVED}${name}"$'\n'
        fi
    done < <(awk '/^## / { sub(/^## /, ""); print }' "$repo_map")
fi

echo "repo_map=$repo_map"
echo "map_headings=$MAP_HEADINGS"
echo "map_repos=$MAP_REPOS"
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

if [ -n "$MAP_UNRESOLVED" ]; then
    printf '=== map unresolved ===\n%s\n' "$MAP_UNRESOLVED"
fi

cat "$DONE_FILE"
