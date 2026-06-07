---
name: close-daily-note
description: Summarize a day's work in a project's daily note and optionally set up the next day's note. Use when Christian says "close the daily note", "wrap up the day", "summarize today/yesterday", "what did I do today", or "set up tomorrow's note", or otherwise asks to recap daily progress or finish the current daily note.
---

# Close Daily Note

Generate a narrative summary of a day's work, append it to the daily note, and (when appropriate) create the next day's note with tasks carried forward.

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

Once the target date is resolved, issue a single Bash call that computes every date value used downstream. Reuse these values in Steps 8 and 10 instead of calling `date` again (macOS only):

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

Read the full daily note. Verify it has a `# Notes` section. If it doesn't, tell the user the note is missing the Notes section and stop (nowhere to insert the summary, and a missing Notes section signals this is not a structured project daily note).

If the Notes section already contains a `## Generated daily summary` sub-section, a summary was already written for this date. Warn the user and ask whether to replace it or skip.

Extract:

- **Pomodoros**: count, task names, categories. Note which tasks had multiple pomodoros (sustained focus).
- **Completed tasks**: lines matching `- [x]` in the Next tasks section.
- **In-progress tasks**: unchecked tasks (`- [ ]`) that have at least one checked sub-task beneath them.
- **Notes section**: any existing content (the summary will be appended here).

### Step 4: Gather git commits

Some projects track work across several repositories and declare them in a repository map. Others keep their work in a single repo (often the project itself). Detect which case applies.

Look for a repository map under the project root:

```bash
find "$PROJECT_ROOT" -maxdepth 4 -name "Repository map.md"
```

**If a repository map is found**, read it and extract repos:

- Repo names come from `##` headings whose name corresponds to a directory under the parent of the project root (`$(dirname "$PROJECT_ROOT")`, i.e., sibling projects).
- Skip headings that are not repositories (e.g., `## Shared patterns`).
- Verify each candidate directory exists before running git log. If a directory is missing, warn the user (mention which one) and continue with the rest. If fewer than two valid repos remain, the map or the paths are likely wrong. Stop and tell the user.

**If no repository map is found**, default to the project's own repository: use `PROJECT_ROOT` if it is a git repository. If it is not a git repository, skip the git step entirely and build the summary from the pomodoro and task data alone (mention in the summary that no commits were available).

For each resolved repo, run:
```bash
git -C <repo-path> log --after="YYYY-MM-DDT00:00:00" --before="YYYY-MM-DDT23:59:59" --oneline --branches
```

`--branches` counts commits on any local branch that day, so work done on an unmerged feature branch is not silently dropped. The date range keeps it to that day. Collect the commit messages, de-duplicating any that appear on more than one branch. Skip repos with no commits on that date.

If there are zero commits across all repos AND zero pomodoros in the daily note, there is nothing to summarize. Tell the user and stop.

### Step 4.5: Load the writing style skill

Load the `christian-writing-style` skill before proceeding. The summary must match Christian's voice.

### Step 5: Write the summary

Write a summary as a bullet list in Christian's writing style (direct, concise, no filler). Each bullet should be a sentence or two covering a coherent group of related work. Don't create one bullet per commit or one per pomodoro. Instead, group related items together so each bullet tells a small story.

The summary should cover:

- What the main focus was. Pomodoro tasks and their categories are the primary signal for what the day was about. Commits corroborate and add detail, but the pomodoro log defines the narrative arc.
- What was accomplished, tying together pomodoro tasks, completed checklist items, and commits into coherent groups
- What kind of work the commits represent (new code, refactoring, documentation, infrastructure). When several repos saw activity, note which did what.
- If tasks were started but not finished, where things stand
- What's queued up next based on incomplete tasks and the Next tasks section

Aim for 3-6 bullets. No headers within the summary. No filler phrases like "productive day" or "good progress was made." Do not use semicolons or em-dashes in the summary text.

### Step 6: Append to the daily note

Insert the summary under a `## Generated daily summary` sub-section within the `# Notes` section of the daily note. If the Notes section already has other content, append the new sub-section below it with a blank line separator. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents in the same vault are fine if relevant.

### Step 7: Confirm the summary

Tell the user the summary was written and point to the daily note's file path. Do not echo the summary content in the conversation: the user will review it directly in the file.

## Part 2: Create the next day's note

This part always runs after Part 1, regardless of how far back the target date is. This supports cascading catch-up: if multiple days need closing, run the skill once per day in sequence and each run creates the next day's note. Step 9 guards against overwriting an existing note.

### Step 8: Determine the next day's date

Use `next_day` from the batched call in Step 1.

### Step 9: Check that the next day's note does not already exist

Run `find "$DAILY_NOTES_DIR" -maxdepth 2 -name "*YYYY-MM-DD*"` (substitute the next day's date). If a note already exists for the next day, tell the user and skip Part 2. Do not overwrite it.

### Step 10: Create the next day's note from the template

Create the new note at the top level of `DAILY_NOTES_DIR` using the `YYYY-MM-DD Ddd.md` naming convention from Step 2, where `YYYY-MM-DD` is the next day's date from Step 8. Use `next_dow` from the batched call in Step 1 for the day-of-week abbreviation. Do not infer it from the previous day's filename.

Reuse the project's own pomodoro categories rather than hardcoding them. Read the `<!-- Categories: ... -->` comment from the most recent existing note in `DAILY_NOTES_DIR` and copy it verbatim into the template. If no such comment exists, omit the comment line.

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

The template carries all three sections so the new note is structurally complete. The `# Next tasks` heading is part of the template. Write the file so it ends with a newline after `# Next tasks` (the heading on its own line), so Step 11's append starts on a fresh line. Step 11 fills the section with the carried-over tasks rather than re-adding the heading.

### Step 11: Carry over the task list

Append everything after the `# Next tasks` heading from the source daily note (the task lines, not the heading itself, which the template already provides). Confirm the new note ends with a newline first so the append lands on its own line:

```bash
[ -n "$(tail -c 1 "<new-daily-note-path>")" ] && printf '\n' >> "<new-daily-note-path>"
awk 'f { print } /^# Next tasks/ { f = 1 }' "<source-daily-note-path>" >> "<new-daily-note-path>"
```

The task list is a living document. Tasks that were checked off today should remain checked in the carried-over list (they serve as a record of progress). Do not remove completed items or modify the list in any way. The user will curate it manually.

### Step 12: Confirm

Tell the user the next day's note was created (include the path) and that the task list was carried over. Remind the user that no changes were committed. Do not repeat the summary from Step 7.
