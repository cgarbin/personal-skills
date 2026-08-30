#!/usr/bin/env bash
# Builds the next day's note from the source note in one awk pass.
#
# Usage: next-note.sh <source-note> <dest-note> "<YYYY-MM-DD HH:MM>"
# Exit:  0 written, 1 nothing written

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

# Content is buffered and emitted from END, so the output follows a fixed order
# (Pomodoros, Today, Next tasks, Notes, free-form) whatever order the source
# used. An older note with # Notes above # Next tasks still comes out right.
#
# Three kinds of section:
#   - rebuilt:  Pomodoros, from the template plus the source's category comment.
#   - reset:    Today and Notes keep their heading and lose their content, which
#               belongs to the day that is closing.
#   - carried:  Next tasks and any free-form section, verbatim. A free-form
#               section opts into reset behavior with a <!-- day-specific -->
#               comment under its heading, which is how a project resets a
#               heading this script does not know about.
#
# Carried content is copied byte for byte, including any blank lines the user
# put inside it. Only the joins between sections are normalized.
#
# The summary belongs to the source day. Without dropping it explicitly it falls
# through to the free-form tail and the prior recap reappears in the new note.
if ! awk -v now="$NOW" '
  # Drops blank lines from both ends of a buffer, so the joins between sections
  # do not depend on how the source opened and closed each one. Blank lines
  # inside a section belong to the user and stay. No apostrophes in here: the
  # program is single-quoted in the shell.
  function trim_blanks(s,   r) {
    r = s
    sub(/^([ \t]*\n)+/, "", r)
    sub(/(\n[ \t]*)+$/, "", r)
    return (r == "") ? "" : r "\n"
  }
  /^<!-- Categories:/ && !cat_done { cats = $0; cat_done = 1; next }
  # The character class rejects a lone "#" left by a stray keystroke, which
  # occurs in these notes and would otherwise open a junk free-form section that
  # then carries into every later note.
  /^# [^[:space:]]/ {
    heading = tolower($0)
    sub(/[[:space:]]+$/, "", heading)
    if (heading == "# pomodoros")               { phase = "pomodoros"; next }
    if (heading == "# next tasks")              { phase = "tasks";     next }
    if (heading == "# notes")                   { phase = "notes";     next }
    if (heading == "# generated daily summary") { phase = "summary";   next }
    # Prefix match, because the plan section is written as Today, TODAY, and
    # Today s goals across these notes. The heading carries over as written.
    if (heading ~ /^# today/) {
      phase = "today"
      today_heading = $0
      sub(/[[:space:]]+$/, "", today_heading)
      next
    }
    phase = "freeform"
    reset_section = 0
    marker_possible = 1
    # Free-form headings arrive with no guaranteed blank line above them.
    if (freeform != "" && freeform !~ /\n\n$/) freeform = freeform "\n"
    freeform = freeform $0 "\n"
    next
  }
  phase == "tasks" { tasks = tasks $0 "\n"; next }
  phase == "freeform" {
    if (marker_possible) {
      if ($0 ~ /^[[:space:]]*$/) { freeform = freeform $0 "\n"; next }
      marker_possible = 0
      if ($0 ~ /^[[:space:]]*<!--[[:space:]]*day-specific[[:space:]]*-->[[:space:]]*$/) {
        reset_section = 1
        freeform = freeform $0 "\n"
        next
      }
    }
    if (!reset_section) freeform = freeform $0 "\n"
    next
  }
  END {
    print "---"
    print "created: " now
    print "---"
    print ""
    print "# Pomodoros"
    print ""
    if (cats != "") print cats
    print "- 🍅 [task:: ] [category:: ] [start:: ]"
    print ""
    if (today_heading != "") {
      print today_heading
      print ""
    }
    print "# Next tasks"
    print ""
    body = trim_blanks(tasks)
    if (body != "") { printf "%s", body; print "" }
    print "# Notes"
    print ""
    body = trim_blanks(freeform)
    if (body != "") printf "%s", body
  }
' "$SOURCE" > "$DEST"; then
    # A failed redirect leaves either nothing or a partial file. Removing it
    # keeps the "already exists" check above from blocking a retry.
    rm -f "$DEST"
    echo "ERROR: could not write $DEST" >&2
    exit 1
fi

echo "wrote $DEST"
