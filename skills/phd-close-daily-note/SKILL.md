---
name: phd-close-daily-note
description: Close out a PhD daily note by generating the daily summary, creating the next day's note from the Obsidian template, and carrying over the task list. Use when Christian says "close out today", "close the daily note", "wrap up the day", "set up tomorrow's note", "close out the day", or any request to finish the current daily note and prepare for the next day.
---

# Close Daily Note

Close out a PhD daily note and prepare the next day's note. This is an end-of-day workflow that chains together several steps: summarizing what happened, creating the next note, and carrying tasks forward.

Do not commit any changes. Leave everything for the user to review.

## Step 1: Generate the daily summary

Invoke the `phd-daily-summary` skill with `today` as the argument. This writes the summary into the current daily note.

If the user provided a specific date argument (e.g., `/phd-close-daily-note 2026-03-25`), use that date instead of today.

## Step 2: Determine the next day's date

Calculate the calendar day after the target date. Handle month and year boundaries correctly:

- 2026-03-31 becomes 2026-04-01
- 2026-12-31 becomes 2027-01-01
- 2026-02-28 becomes 2026-03-01 (2026 is not a leap year)

Format as `YYYY-MM-DD`.

## Step 3: Check that the next day's note does not already exist

Daily notes live in `/Users/cgarbin/projects/phd-dissertation-writing/_daily-notes/`. Check both possible locations:

1. Top level: `_daily-notes/YYYY-MM-DD.md`
2. Monthly subdirectory: `_daily-notes/YYYY-MM/YYYY-MM-DD.md`

If a note already exists for the next day, tell the user and ask whether to overwrite it or skip creating the note (still carry over tasks if the user wants).

## Step 4: Create the next day's note from the template

Create the new note at the top level: `_daily-notes/YYYY-MM-DD.md`. This matches Obsidian's daily notes configuration (`folder: "_daily-notes"`).

The `created` frontmatter field records when the file was physically created, not the date the note is for. Use today's date (the day the skill is running) and the current time in `HH:mm` format. The filename is what identifies which day the note belongs to.

Use this template:

```markdown
---
created: YYYY-MM-DD HH:mm
---

# Today's Focus

-

# Pomodoros
<!-- Categories: writing | lit-review | experiment | analysis | admin -->
- [ ] 🍅 [task:: ] [category:: writing | lit-review | experiment | analysis | admin] [start:: ]

# Notes

# Next tasks
```

## Step 5: Carry over the task list

Read the `# Next tasks` section from the day being closed out. Copy it into the new note's `# Next tasks` section, preserving all content: headers, numbering, indentation, wikilinks, and checkbox states.

The task list is a living document. Tasks that were checked off today should remain checked in the carried-over list (they serve as a record of progress). Do not remove completed items or modify the list in any way. The user will curate it manually.

## Step 6: Confirm

Tell the user what was done:

- The daily summary was generated (show it briefly or reference the skill output)
- The next day's note was created at the path
- The task list was carried over

Remind the user that no changes were committed.
