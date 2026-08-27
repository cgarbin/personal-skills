#!/usr/bin/env bash
# Removes an existing "# Generated daily summary" section from a note, in place,
# so a fresh one can be inserted with the same Edit as a first run.
#
# This is a script rather than an Edit because deleting the section by hand
# needs an exact match over generated prose from an earlier run, which is the
# most failure-prone step in the skill.
#
# Only the summary section changes. Blank lines elsewhere stay as the user wrote
# them, and a note with no summary section is left byte for byte alone.
#
# Usage: strip-summary.sh <note>
# Exit:  0 the note has no summary section, whether it had one or not
#        1 error, note left unchanged

NOTE="${1:-}"

if [ -z "$NOTE" ]; then
    echo "usage: strip-summary.sh <note>" >&2
    exit 1
fi
if [ ! -f "$NOTE" ]; then
    echo "ERROR: $NOTE does not exist" >&2
    exit 1
fi
if ! grep -qiE '^# generated daily summary[[:space:]]*$' "$NOTE"; then
    echo "no summary section in $NOTE, left unchanged"
    exit 0
fi

# The temp file sits beside the note so the swap is a same-filesystem rename,
# which cannot leave the note half-written the way a redirect onto it could.
# The leading dot keeps Obsidian from indexing it if the run dies first.
TMP=$(mktemp "$(dirname "$NOTE")/.close-daily-note.XXXXXX") || exit 1

if ! awk '
  # Every top-level heading reassigns skip, so the section ends at the next one.
  # The character class rejects a lone "#" left by a stray keystroke.
  /^# [^[:space:]]/ {
    heading = tolower($0)
    sub(/[[:space:]]+$/, "", heading)
    skip = (heading == "# generated daily summary")
  }
  !skip
' "$NOTE" > "$TMP"; then
    echo "ERROR: could not rewrite $NOTE, left unchanged (partial output in $TMP)" >&2
    exit 1
fi

# An empty result means awk ate the note rather than one section of it.
if [ ! -s "$TMP" ]; then
    rm -f "$TMP"
    echo "ERROR: rewriting $NOTE produced an empty file, left unchanged" >&2
    exit 1
fi

# mktemp creates the file 0600, so carry the note's own mode across the rename.
chmod "$(stat -f '%Lp' "$NOTE")" "$TMP" 2>/dev/null || true

if ! mv "$TMP" "$NOTE"; then
    echo "ERROR: could not replace $NOTE, left unchanged (new version in $TMP)" >&2
    exit 1
fi

echo "stripped summary section from $NOTE"
