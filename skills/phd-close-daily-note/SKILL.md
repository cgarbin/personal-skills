---
name: phd-close-daily-note
description: Summarize a day's PhD work and optionally prepare the next day's note. Use when Christian says "close out today", "close the daily note", "wrap up the day", "set up tomorrow's note", "summarize today", "summarize yesterday", "what did I do today/yesterday", "write a daily summary", or any request to recap daily progress or finish the current daily note.
---

# Close Daily Note

Generate a narrative summary of a day's work, append it to the daily note, and (when appropriate) create the next day's note with tasks carried forward.

Do not commit any changes. Leave everything for the user to review.

## Part 1: Generate the daily summary

### Step 0: Load the writing style skill

Load the `christian-writing-style` skill before proceeding. The summary must match Christian's voice.

### Step 1: Determine the target date

If the user provided a date as an argument (e.g., `/phd-close-daily-note yesterday`, `/phd-close-daily-note 2026-03-15`), use that date. Otherwise, default to yesterday.

Date interpretation:

- "today": use the current date
- "yesterday" or no date specified: use the day before the current date
- A specific date like "March 15" or "2026-03-15": use that date

Convert to `YYYY-MM-DD` format. If the date is in the future, tell the user and stop. Confirm with the user before proceeding if there is any ambiguity (e.g., "last Friday" when you're unsure which Friday).

### Step 2: Find the daily note

Daily notes live in `/Users/cgarbin/projects/phd-dissertation-writing/_daily-notes/`. Filenames follow the pattern `YYYY-MM-DD Ddd.md` (e.g., `2026-04-02 Thu.md`). Older notes may be in a monthly subdirectory (`_daily-notes/YYYY-MM/`).

Glob for `_daily-notes/*YYYY-MM-DD*` and `_daily-notes/YYYY-MM/*YYYY-MM-DD*` to find the file. If the note doesn't exist, tell the user and stop.

### Step 3: Read the daily note

Read the full daily note. Verify it has a `# Notes` section. If it doesn't, tell the user the note is missing the Notes section and stop (nowhere to insert the summary).

If the Notes section already contains a `## Generated daily summary` sub-section, a summary was already written for this date. Warn the user and ask whether to replace it or skip.

Extract:

- **Pomodoros**: count, task names, categories. Note which tasks had multiple pomodoros (sustained focus).
- **Completed tasks**: lines matching `- [x]` in the Next tasks section.
- **In-progress tasks**: unchecked tasks (`- [ ]`) that have at least one checked sub-task beneath them.
- **Notes section**: any existing content (the summary will be appended here).

### Step 4: Gather git commits across all repositories

Read the repository map at `/Users/cgarbin/projects/phd-dissertation-writing/PhD dissertation - temporal EHR summary/Supporting material/Repository map.md` to get the current list of repositories. All repositories live under `~/projects/`. Extract the repository names from the `##` headings where the heading name corresponds to a directory under `~/projects/`. Skip headings that are not repositories (e.g., `## Shared patterns`).

For each candidate repo, verify the directory exists on disk before running git log. If a directory is missing, warn the user (mention which one) but continue with the remaining repos. If fewer than three valid repos are found after verification, something is wrong with the repository map or the paths. Stop and tell the user.

For each repo, run:
```bash
git -C <repo-path> log --after="YYYY-MM-DDT00:00:00" --before="YYYY-MM-DDT23:59:59" --oneline main
```

Collect the commit messages. Skip repos with no commits on that date.

If there are zero commits across all repos AND zero pomodoros in the daily note, there is nothing to summarize. Tell the user and stop.

### Step 5: Write the summary

Write a summary as a bullet list in Christian's writing style (direct, concise, no filler). Each bullet should be a sentence or two covering a coherent group of related work. Don't create one bullet per commit or one per pomodoro. Instead, group related items together so each bullet tells a small story.

The summary should cover:

- What the main focus was. Pomodoro tasks and their categories are the primary signal for what the day was about. Commits corroborate and add detail, but the pomodoro log defines the narrative arc.
- What was accomplished, tying together pomodoro tasks, completed checklist items, and commits into coherent groups
- Which repos saw activity and what kind (new code, refactoring, documentation, infrastructure)
- If tasks were started but not finished, where things stand
- What's queued up next based on incomplete tasks or the Next tasks section, if it exists

Aim for 3-6 bullets. No headers within the summary. No filler phrases like "productive day" or "good progress was made." Do not use semicolons or em-dashes in the summary text.

### Step 6: Append to the daily note

Insert the summary under a `## Generated daily summary` sub-section within the `# Notes` section of the daily note. If the Notes section already has other content, append the new sub-section below it with a blank line separator. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents like `[[CareVue MetaVision decision]]` are fine if relevant.

### Step 7: Confirm the summary

Tell the user the summary was written and show it in the conversation so they can review it without opening the file.

## Part 2: Create the next day's note

This part always runs after Part 1, regardless of how far back the target date is. This supports cascading catch-up: if multiple days need closing, run the skill once per day in sequence and each run creates the next day's note. Step 9 guards against overwriting an existing note.

### Step 8: Determine the next day's date

Compute the next calendar day using `date -j -v+1d -f "%Y-%m-%d" "YYYY-MM-DD" "+%Y-%m-%d"` (macOS). Do not compute date arithmetic manually.

### Step 9: Check that the next day's note does not already exist

Glob for `_daily-notes/*YYYY-MM-DD*` and `_daily-notes/YYYY-MM/*YYYY-MM-DD*`. If a note already exists for the next day, tell the user and skip Part 2. Do not overwrite it.

### Step 10: Create the next day's note from the template

Create the new note at the top level using the `YYYY-MM-DD Ddd.md` naming convention from Step 2, where `YYYY-MM-DD` is the next day's date from Step 8. Compute the day-of-week abbreviation with `date -j -f "%Y-%m-%d" "<next-day-date>" "+%a"` (macOS). Do not infer it from the previous day's filename.

Use this template. The `created` field uses today's date and current time (when the file is physically created), not the note's target date:

```markdown
---
created: YYYY-MM-DD HH:mm
---

# Pomodoros
<!-- Categories: writing | lit-review | experiment | analysis | admin -->
- [ ] 🍅 [task:: ] [category:: writing | lit-review | experiment | analysis | admin] [start:: ]

# Notes

# Next tasks
```

### Step 11: Carry over the task list

Copy the `# Next tasks` section (already read in Step 3) into the new note's `# Next tasks` section, preserving all content: headers, numbering, indentation, wikilinks, and checkbox states.

The task list is a living document. Tasks that were checked off today should remain checked in the carried-over list (they serve as a record of progress). Do not remove completed items or modify the list in any way. The user will curate it manually.

### Step 12: Confirm

Tell the user the next day's note was created (include the path) and that the task list was carried over. Remind the user that no changes were committed. Do not repeat the summary from Step 7.
