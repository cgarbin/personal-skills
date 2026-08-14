#!/usr/bin/env bash
# Builds the next day's note from the source note in one awk pass.
#
# Usage: next-note.sh <source-note> <dest-note> "<YYYY-MM-DD HH:MM>"
# Exit:  0 written, 1 nothing written

set -o pipefail

SOURCE="${1:-}"
DEST="${2:-}"
NOW="${3:-}"

if [ -z "$SOURCE" ] || [ -z "$DEST" ] || [ -z "$NOW" ]; then
    echo "usage: next-note.sh <source-note> <dest-note> \"<YYYY-MM-DD HH:MM>\"" >&2
    exit 1
fi
if [ ! -f "$SOURCE" ]; then
    echo "ERROR: source note $SOURCE does not exist" >&2
    exit 1
fi
# The carried-over task list is the user's to curate, so a second run must not
# discard edits they made to a note this script already produced.
if [ -e "$DEST" ]; then
    echo "ERROR: $DEST already exists, refusing to overwrite" >&2
    exit 1
fi
# Without this the awk below emits an empty Next tasks section and the run looks
# like it worked, which loses the carryover silently.
if ! grep -qiE '^# next tasks[[:space:]]*$' "$SOURCE"; then
    echo "ERROR: $SOURCE has no '# Next tasks' heading, nothing to carry over" >&2
    exit 1
fi

# Content is buffered and emitted from END, so the output follows canonical
# order (Pomodoros, Next tasks, Notes, free-form) whatever order the source
# used. An older note with # Notes above # Next tasks still comes out right.
#
# The Notes heading carries over without its content, which is day-specific.
if ! awk -v now="$NOW" '
  /^<!-- Categories:/ && !cat_done { cats = $0; cat_done = 1; next }
  /^# / {
    h = tolower($0)
    if (h ~ /^# pomodoros[[:space:]]*$/)  { phase = "pomodoros"; next }
    if (h ~ /^# next tasks[[:space:]]*$/) { phase = "tasks";     next }
    if (h ~ /^# notes[[:space:]]*$/)      { phase = "notes";     next }
    # The summary belongs to the source day. Without this it falls through to
    # the free-form tail and the prior recap reappears in the new note.
    if (h ~ /^# generated daily summary[[:space:]]*$/) { phase = "summary"; next }
    # Any other top-level heading starts the free-form tail, which keeps its
    # own headings.
    phase = "freeform"
    freeform = freeform $0 "\n"
    next
  }
  phase == "tasks"    { tasks = tasks $0 "\n" }
  phase == "freeform" { freeform = freeform $0 "\n" }
  END {
    print "---"
    print "created: " now
    print "---"
    print ""
    print "# Pomodoros"
    print ""
    if (cats != "") print cats
    print "- [ ] 🍅 [task:: ] [category:: ] [start:: ]"
    print ""
    print "# Next tasks"
    print ""
    printf "%s", tasks
    print ""
    print "# Notes"
    print ""
    printf "%s", freeform
  }
' "$SOURCE" | cat -s > "$DEST"; then
    # A failed redirect leaves either nothing or a partial file. Removing it
    # keeps the existence guard above from blocking the retry.
    rm -f "$DEST"
    echo "ERROR: could not write $DEST" >&2
    exit 1
fi

echo "wrote $DEST"
