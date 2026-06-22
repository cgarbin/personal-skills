---
name: close-daily-note
description: Summarize a day's work in a project's daily note and optionally set up the next day's note. Use when Christian says "close the daily note", "wrap up the day", "summarize today/yesterday", "what did I do today", or "set up tomorrow's note", or otherwise asks to recap daily progress or finish the current daily note.
---

# Close Daily Note

Generate a narrative summary of a day's work, append it to the daily note, and create the next day's note when one doesn't already exist.

This skill works for any project that keeps daily notes in the structured format: a `_daily-notes/` directory, notes named `YYYY-MM-DD Ddd.md`, and `# Pomodoros`, `# Next tasks`, and `# Notes` sections inside each note. It resolves the project from the current session rather than any hardcoded path. If the current location has no such daily notes, it stops (Step 0), which keeps it from firing on free-form journals or non-daily-note projects.

Do not commit any changes. Leave everything for the user to review.

## Canonical section order

Daily notes follow this top-level section order, and the skill produces output that conforms to it:

1. `# Generated daily summary` (added by Step 7, missing until then)
2. `# Pomodoros`
3. `# Next tasks`
4. `# Notes`
5. Free-form sections (any other top-level headings, in the order they appear)

Step 7 inserts the summary at the top of the source note so it is the first thing the user sees. Step 8 builds the next day's note: it emits sections 2-4 in canonical order, carries section 3 (Next tasks) and any free-form sections from (5) verbatim, and skips the Notes section's *content*, which is day-specific. The `# Notes` heading itself carries over as an empty stub so the new note's structure is complete from the start.

## Step 0: Resolve the project's daily-notes directory (run first)

The skill operates on the daily notes of the current project. Resolve the directory once and reuse it everywhere below as `DAILY_NOTES_DIR`.

- If the user named a project or passed a path, use it. Set `PROJECT_ROOT` to the project root and `DAILY_NOTES_DIR` to `$PROJECT_ROOT/_daily-notes`.
- Otherwise, walk up from the current working directory to find the nearest ancestor containing a `_daily-notes/` directory:

```bash
dir="$PWD"
while [ "$dir" != "/" ]; do
  if [ -d "$dir/_daily-notes" ]; then
    echo "PROJECT_ROOT=$dir"
    echo "DAILY_NOTES_DIR=$dir/_daily-notes"
    break
  fi
  dir=$(dirname "$dir")
done
```

If no `_daily-notes/` directory is found, tell the user you could not locate a project daily-notes directory from the current location and ask them to `cd` into the project (or name it). Stop. Record `PROJECT_ROOT` and `DAILY_NOTES_DIR` for the steps below.

## Part 1: Generate the daily summary

### Step 1: Determine the target date

Resolve the target date from the user's request. Do not rely on session metadata or context-injected dates.

- No argument or "yesterday": day before today.
- "today": today.
- Specific date ("March 15", "2026-03-15"): that date.

Convert to `YYYY-MM-DD`. If the date is in the future, tell the user and stop. If ambiguous ("last Friday" with two plausible Fridays), confirm before proceeding.

Once the target date is resolved, issue a single Bash call that computes every date value used downstream, including today's date. Reuse these values in Step 8 instead of calling `date` again (macOS only):

```bash
TARGET="<resolved YYYY-MM-DD>"
echo "today=$(date '+%Y-%m-%d')"
echo "now=$(date '+%Y-%m-%d %H:%M')"
echo "next_day=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%Y-%m-%d')"
echo "next_dow=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%a')"
```

These values are literals to substitute into later Bash calls. Each Bash invocation is a fresh shell, so the agent passes them inline (e.g., `awk -v now="2026-06-13 07:46" ...`).

### Step 2: Find the daily note

Daily notes live in `DAILY_NOTES_DIR` (from Step 0). Filenames follow the pattern `YYYY-MM-DD Ddd.md` (e.g., `2026-04-02 Thu.md`). Older notes may be in a monthly subdirectory (`_daily-notes/YYYY-MM/`) or a yearly one (`_daily-notes/YYYY/`).

Run `find "$DAILY_NOTES_DIR" -maxdepth 2 -name "*YYYY-MM-DD*"` (substitute the actual date). The `-maxdepth 2` covers both the top-level directory and any `YYYY-MM/` or `YYYY/` subdirectory in one pass. If the note doesn't exist, tell the user and stop.

### Step 3: Read the daily note

Read the full daily note. Verify it has both a `# Notes` section and a `# Next tasks` section. If `# Notes` is missing, tell the user and stop (a missing Notes section signals this is not a structured project daily note). If `# Next tasks` is missing, tell the user and stop (Step 8 reads from this section, and a missing heading would silently produce an empty carryover). Heading matches are case-insensitive but must be top-level (`# `, not `## `), with optional trailing whitespace allowed.

If the file already contains a top-level `# Generated daily summary` section, a summary was already written for this date. Warn the user and ask whether to replace it or skip.

From the file you just read, extract four signals directly. These feed the Step 4 stop condition and scaffold the Step 6 summary. No shell call: parse the text you already have.

- **Pomodoros**: count of lines under `# Pomodoros` that match the pomodoro template *and have content in the task field*. The template form is `- [ ] 🍅 [task:: ...] [category:: ...] [start:: ...]`. A line counts only when `[task:: ...]` contains at least one non-space, non-`]` character (the empty stub `[task:: ]` does not count). Both checked (`[x]`) and unchecked (`[ ]`) pomodoros count.
- **Done tasks**: lines under `# Next tasks` that are checked off. Match either bullet style: `- [x]` *or* numbered like `1. [x]`, `2. [x]`, with optional leading whitespace for nesting. Capture the full line text.
- **Open tasks**: same as above but `[ ]` instead of `[x]`. Used for scaffolding only, not for the stop condition.
- **Notes lines**: count of non-empty lines under `# Notes` (excluding the heading itself).

Section boundaries are top-level headings (`# `, not `## `) with optional trailing whitespace. Match heading names case-insensitively.

These four signals are the only structured input Step 4 needs. The full Notes content for the Step 6 summary comes straight from the Read output.

### Step 4: Gather git commits

The loop below needs two values: `TARGET`, the target date resolved in Step 1, and `REPOS`, set per the cases below. Variables do not carry across separate Bash calls, so assign both in the same call as the loop.

**Which repos to run it on:**

Detect the multi-repo case first. Look for a repository map under the project root:

```bash
find "$PROJECT_ROOT" -maxdepth 4 -name "Repository map.md"
```

Set `REPOS` per case:

- **Multi-repo (map found)**: extract candidate repo names from `##` headings in the map and keep only the ones that exist as sibling directories with a `.git`:
  ```bash
  parent=$(dirname "$PROJECT_ROOT")
  REPOS=()
  while IFS= read -r name; do
    path="$parent/$name"
    if [ -d "$path/.git" ]; then
      REPOS+=("$path")
    else
      echo "MISSING or not a git repo: $name"
    fi
  done < <(awk '/^## / { sub(/^## /, ""); print }' "$repo_map")
  ```
  Warn the user about any `MISSING` line and continue with the rest. If fewer than two valid repos remain, the map or the paths are likely wrong. Stop and tell the user.
- **Single-repo (no map, `PROJECT_ROOT` is a git repository)**: `REPOS=("$PROJECT_ROOT")`.
- **No git (no map, `PROJECT_ROOT` is not a git repository)**: skip the loop entirely. The summary will rely on the pomodoro, task, and Notes data from Step 3.

**Gather:**

```bash
for repo_path in "${REPOS[@]}"; do
  commits=$(git -C "$repo_path" log \
    --after="${TARGET}T00:00:00" --before="${TARGET}T23:59:59" \
    --oneline --branches)
  if [ -n "$commits" ]; then
    printf '=== %s ===\n%s\n\n' "$repo_path" "$commits"
  fi
done
```

`--branches` counts commits on any local branch that day, so work on an unmerged feature branch is not silently dropped. De-duplicate any commit that appears on more than one branch.

**Stop condition:**

Stop only when *all* of the following are true: zero commits from this step, zero pomodoros from Step 3, zero done tasks from Step 3, and zero notes lines from Step 3. If any one has content, proceed to Step 5.

### Step 5: Load the writing style skill

Load the `christian-writing-style` skill before proceeding. The summary must match Christian's voice.

### Step 6: Write the summary

Write a summary as a bullet list in Christian's writing style (direct, concise, no filler). Each bullet should be a sentence or two covering a coherent group of related work. Don't create one bullet per commit or one per pomodoro. Group related items together so each bullet tells a small story.

The summary should answer:

- What the main focus was.
- What was completed.
- What's still open or in progress.

Do not summarize what's queued next. The Next tasks section is carried over verbatim into the next day's note in Step 8, so restating it in prose duplicates the same information.

Use whatever signal is present. Pomodoros, commits, checked tasks, and the Notes section each contribute when available, and the summary gets thinner when fewer of them have content. Resist filling in detail the source does not provide.

When extra signal is present, also note:

- **Pomodoros**: what defined the day's narrative arc, especially tasks with multiple pomodoros (sustained focus).
- **Commits**: what kind of work they represent (new code, refactoring, documentation, infrastructure). When several repos saw activity, note which did what.

Use plain past-tense narration of what was completed. Do not invent times, ordering, or causality that the source does not support.

Let the day's content set the length. One bullet per coherent group of work, not one per commit or task. If the day has two stories, write two bullets. If it has five, write five. Stop when you've covered the day honestly. No headers within the summary. No filler phrases like "productive day" or "good progress was made." Do not use semicolons or em-dashes in the summary text.

### Step 7: Insert the summary at the top of the daily note

Insert the summary as a top-level `# Generated daily summary` section, placed after the YAML frontmatter and before `# Pomodoros`. The summary is the first thing the user sees when opening the note.

Use Edit with `# Pomodoros` as the anchor. Replace `# Pomodoros` with the new summary block followed by `# Pomodoros`:

```
# Generated daily summary

<bullets from Step 6>

# Pomodoros
```

If a `# Generated daily summary` section already exists (Step 3 detected it and the user chose to replace), remove the old section first with a separate Edit that deletes from `# Generated daily summary` through the blank line before `# Pomodoros`. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents in the same vault are fine if relevant.

## Part 2: Create the next day's note

This part always runs after Part 1, regardless of how far back the target date is. This supports cascading catch-up: if multiple days need closing, run the skill once per day in sequence and each run creates the next day's note.

The skill is meant to close days that have real content. When catching up over several days, expect runs for empty intermediate days to trip the Step 4 stop condition, which is the correct behavior. Skip those days rather than fabricating content for them.

### Step 8: Create the next day's note

Compute the new note path from `next_day` and `next_dow` (from Step 1's batched call). The filename is `YYYY-MM-DD Ddd.md` at the top level of `DAILY_NOTES_DIR`. The new note always goes at the top level even if the source note lived in a `YYYY-MM/` or `YYYY/` archive subdirectory. If the file already exists, tell the user and skip the rest of Part 2. Do not overwrite it. Skipping forgoes task carryover; the user can merge manually if needed.

Otherwise, build the entire new note in one awk pass over the source. The pass emits, in order:

1. Frontmatter with `created: <now>`.
2. `# Pomodoros` heading, the source's `<!-- Categories: ... -->` comment if present, and a blank pomodoro template line.
3. `# Next tasks` heading, followed by the source's task lines (between `# Next tasks` and the next top-level heading).
4. `# Notes` heading, followed by everything after `# Notes` in the source up to EOF.

```bash
awk -v now="$now" '
  function emit_pomodoro_template() {
    if (!emitted) {
      print "- [ ] 🍅 [task:: ] [category:: ] [start:: ]"
      print ""
      emitted = 1
    }
  }
  BEGIN {
    print "---"
    print "created: " now
    print "---"
    print ""
    print "# Pomodoros"
  }
  /^<!-- Categories:/ && !cat_done { print; cat_done = 1; next }
  /^# / {
    h = tolower($0)
    if (h ~ /^# next tasks[[:space:]]*$/) { emit_pomodoro_template(); phase = "tasks"; print "# Next tasks\n"; next }
    if (h ~ /^# notes[[:space:]]*$/)      { emit_pomodoro_template(); phase = "skip";  print "\n# Notes\n";    next }
    if (phase == "tasks" || phase == "skip") { phase = "freeform"; print; next }
  }
  phase == "tasks" || phase == "freeform" { print }
' "<source-daily-note-path>" | cat -s > "<new-daily-note-path>"
```

One blank like after each heading: The `\n` in `print "# Next tasks\n"` and `print "\n# Notes\n"` guarantees at least one blank line after each heading even when the source has none. The `cat -s` collapses any run of consecutive blank lines down to one.

The Notes section itself is day-specific and is not carried over. The awk keys off heading names, not position, so an older source note with `# Notes` before `# Next tasks` still produces a correctly-ordered output. If the source has no Categories comment, `emit_pomodoro_template()` still fires when the first carryover heading is hit, so the Pomodoros section is structurally complete.

The task list is a living document. Tasks that were checked off in the source note should remain checked in the carried-over list. Do not remove completed items or modify the list in any way. The user will curate it manually.

## Final report

At the end of the run, tell the user where the summary was written. Do not echo the summary content in the conversation: the user will review it directly in the file. If Part 2 created a new note, add its path and mention that the task list was carried over. Remind the user that no changes were committed.
