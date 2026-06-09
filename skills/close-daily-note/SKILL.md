---
name: close-daily-note
description: Summarize a day's work in a project's daily note and optionally set up the next day's note. Use when Christian says "close the daily note", "wrap up the day", "summarize today/yesterday", "what did I do today", or "set up tomorrow's note", or otherwise asks to recap daily progress or finish the current daily note.
---

# Close Daily Note

Generate a narrative summary of a day's work, append it to the daily note, and create the next day's note when one doesn't already exist.

This skill works for any project that keeps daily notes in the structured format: a `_daily-notes/` directory, notes named `YYYY-MM-DD Ddd.md`, and `# Pomodoros`, `# Notes`, and `# Next tasks` sections inside each note. It resolves the project from the current session rather than any hardcoded path. If the current location has no such daily notes, it stops (Step 0), which keeps it from firing on free-form journals or non-daily-note projects.

Do not commit any changes. Leave everything for the user to review.

## Step 0: Resolve the project's daily-notes directory (run first)

The skill operates on the daily notes of the current project. Resolve the directory once and reuse it everywhere below as `DAILY_NOTES_DIR`.

- If the user named a project or passed a path, use it. Set `DAILY_NOTES_DIR` to that `_daily-notes` directory and `PROJECT_ROOT` to its parent directory.
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

Run `date "+%Y-%m-%d"` (macOS) for today. Do not rely on session metadata or context-injected dates.

Resolve the target date:

- No argument or "yesterday": day before today.
- "today": today.
- Specific date ("March 15", "2026-03-15"): that date.

Convert to `YYYY-MM-DD`. If the date is in the future, tell the user and stop. If ambiguous ("last Friday" with two plausible Fridays), confirm before proceeding.

Once the target date is resolved, issue a single Bash call that computes every date value used downstream. Reuse these values in Step 8 instead of calling `date` again (macOS only):

```bash
TARGET="<resolved YYYY-MM-DD>"
echo "today=$(date '+%Y-%m-%d')"
echo "now=$(date '+%Y-%m-%d %H:%M')"
echo "next_day=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%Y-%m-%d')"
echo "next_dow=$(date -j -v+1d -f '%Y-%m-%d' "$TARGET" '+%a')"
```

### Step 2: Find the daily note

Daily notes live in `DAILY_NOTES_DIR` (from Step 0). Filenames follow the pattern `YYYY-MM-DD Ddd.md` (e.g., `2026-04-02 Thu.md`). Older notes may be in a monthly subdirectory (`_daily-notes/YYYY-MM/`) or a yearly one (`_daily-notes/YYYY/`).

Run `find "$DAILY_NOTES_DIR" -maxdepth 2 -name "*YYYY-MM-DD*"` (substitute the actual date). The `-maxdepth 2` covers both the top-level directory and any `YYYY-MM/` or `YYYY/` subdirectory in one pass. If the note doesn't exist, tell the user and stop.

### Step 3: Read the daily note

Read the full daily note. Verify it has both a `# Notes` section and a `# Next tasks` section. If `# Notes` is missing, tell the user and stop (nowhere to insert the summary, and a missing Notes section signals this is not a structured project daily note). If `# Next tasks` is missing, tell the user and stop (Step 9 reads from this section, and a missing heading would silently produce an empty carryover).

If the Notes section already contains a `## Generated daily summary` sub-section, a summary was already written for this date. Warn the user and ask whether to replace it or skip.

Headings must match `# Pomodoros`, `# Notes`, `# Next tasks` exactly (case and level). Mismatches are treated as missing sections.

Extract:

- **Pomodoros**: count, task names, categories. Note which tasks had multiple pomodoros (sustained focus). A pomodoro counts only if the `[task:: ]` field has content. The template placeholder line does not count, even though the bullet is present.
- **Completed tasks**: lines matching `- [x]` in the Next tasks section.
- **In-progress tasks (heuristic)**: unchecked parent tasks with mixed subtask state (some checked, some not). The Next tasks section does not record activity timestamps, so use it as a snapshot of state, not as a per-day activity log.
- **Notes section**: any existing content (the summary will be appended here).

### Step 4: Gather git commits

First, decide which repos to query. Then run the same git command against each.

**Command to run per repo:**

```bash
git -C "<repo-path>" log --after="YYYY-MM-DDT00:00:00" --before="YYYY-MM-DDT23:59:59" --oneline --branches
```

`--branches` counts commits on any local branch that day, so work done on an unmerged feature branch is not silently dropped. Collect the commit messages, de-duplicating any that appear on more than one branch. Skip repos with no commits on that date.

**Which repos to run it on:**

Detect the multi-repo case first. Look for a repository map under the project root:

```bash
find "$PROJECT_ROOT" -maxdepth 4 -name "Repository map.md"
```

- **Multi-repo (map found)**: read the map and extract repos. Repo names come from `##` headings whose name corresponds to a directory under the parent of the project root (`$(dirname "$PROJECT_ROOT")`, i.e., sibling projects). Skip headings that are not repositories (e.g., `## Shared patterns`). Verify each candidate directory exists before running `git log`. If a directory is missing, warn the user (mention which one) and continue with the rest. If fewer than two valid repos remain, the map or the paths are likely wrong. Stop and tell the user.
- **Single-repo (no map, `PROJECT_ROOT` is a git repository)**: run against `PROJECT_ROOT`.
- **No git (no map, `PROJECT_ROOT` is not a git repository)**: skip the git step entirely. The summary will rely on the pomodoro, task, and Notes data from Step 3.

**Stop condition:**

After the git step, stop only when *all* of the following are true: zero commits, zero pomodoros, no checked tasks, and an empty Notes section. If any one of those has content, proceed to Step 5.

### Step 5: Load the writing style skill

Load the `christian-writing-style` skill before proceeding. The summary must match Christian's voice.

### Step 6: Write the summary

Write a summary as a bullet list in Christian's writing style (direct, concise, no filler). Each bullet should be a sentence or two covering a coherent group of related work. Don't create one bullet per commit or one per pomodoro. Group related items together so each bullet tells a small story.

The summary should answer:

- What the main focus was.
- What was completed.
- What's still open or in progress.
- What's queued next, based on the Next tasks section.

Use whatever signal is present. Pomodoros, commits, checked tasks, and the Notes section each contribute when available, and the summary gets thinner when fewer of them have content. Resist filling in detail the source does not provide.

When extra signal is present, also note:

- **Pomodoros**: what defined the day's narrative arc, especially tasks with multiple pomodoros (sustained focus).
- **Commits**: what kind of work they represent (new code, refactoring, documentation, infrastructure). When several repos saw activity, note which did what.

Use plain past-tense narration of what was completed. Do not invent times, ordering, or causality that the source does not support.

Aim for 3-6 bullets. No headers within the summary. No filler phrases like "productive day" or "good progress was made." Do not use semicolons or em-dashes in the summary text.

Example shape for a no-git, task-only day with one large parent task and a few one-line notes:

```markdown
- Closed out the <feature> work: finished the remaining subtasks and submitted the PR. One subtask is still open and deferred.
- Settled one design question along the way: kept the existing serialization approach after a review pass.
- Handled the standing review item and gave feedback on the team's proposal doc.
- Queued for next: a working-group discussion item, a boundary bug, and a stats pull for the upcoming size change.
```

### Step 7: Append to the daily note

Insert the summary under a `## Generated daily summary` sub-section within the `# Notes` section of the daily note. If the Notes section already has other content, append the new sub-section below it with a blank line separator. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents in the same vault are fine if relevant.

## Part 2: Create the next day's note

This part always runs after Part 1, regardless of how far back the target date is. This supports cascading catch-up: if multiple days need closing, run the skill once per day in sequence and each run creates the next day's note.

The skill is meant to close days that have real content. When catching up over several days, expect runs for empty intermediate days to trip the Step 4 stop condition, which is the correct behavior. Skip those days rather than fabricating content for them.

### Step 8: Create the next day's note from the template

Use `next_day` and `next_dow` from the batched call in Step 1. First, check that a note for the next day does not already exist:

```bash
find "$DAILY_NOTES_DIR" -maxdepth 2 -name "*<next_day>*"
```

If one exists, tell the user and skip the rest of Part 2. Do not overwrite it. Note that skipping forgoes task carryover. If the existing note was created manually and needs the task list from the source note, the user must merge it themselves.

Otherwise, create the new note at the top level of `DAILY_NOTES_DIR` using the `YYYY-MM-DD Ddd.md` naming convention. Use `next_dow` for the day-of-week abbreviation. Do not infer it from the previous day's filename.

Reuse the project's own pomodoro categories rather than hardcoding them. Read the `<!-- Categories: ... -->` comment from the note with the latest filename date in `DAILY_NOTES_DIR` (the comment lives directly under the `# Pomodoros` heading) and copy it verbatim into the template. Use filename date, not file mtime, since synced storage (e.g., OneDrive) can scramble mtimes. If no such comment exists, omit the comment line.

Use this template. For the `created` field, use `now` from the batched call in Step 1. Substitute the detected categories comment for the `<!-- Categories: ... -->` line:

```markdown
---
created: YYYY-MM-DD HH:mm
---

# Pomodoros
<!-- Categories: ... -->
- [ ] 🍅 [task:: ] [category:: ] [start:: ]

# Notes

# Next tasks
```

The template carries all three sections so the new note is structurally complete. The `# Next tasks` heading is part of the template. Write the file so it ends with a newline after `# Next tasks` (the heading on its own line), so Step 9's append starts on a fresh line. Step 9 fills the section with the carried-over tasks rather than re-adding the heading.

### Step 9: Carry over the task list

Append everything after the `# Next tasks` heading from the source daily note (the task lines, not the heading itself, which the template already provides). Confirm the new note ends with a newline first so the append lands on its own line:

```bash
[ -n "$(tail -c 1 "<new-daily-note-path>")" ] && printf '\n' >> "<new-daily-note-path>"
awk 'f { print } /^# Next tasks/ { f = 1 }' "<source-daily-note-path>" >> "<new-daily-note-path>"
```

The task list is a living document. Tasks that were checked off in the source note should remain checked in the carried-over list (they serve as a record of progress). Do not remove completed items or modify the list in any way. The user will curate it manually.

## Final report

At the end of the run, tell the user where the summary was written. Do not echo the summary content in the conversation: the user will review it directly in the file. If Part 2 created a new note, add its path and mention that the task list was carried over. Remind the user that no changes were committed.
