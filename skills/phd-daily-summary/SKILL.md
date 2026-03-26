---
name: phd-daily-summary
description: Summarize a day's PhD work by mining the daily note and git commits across all repositories. Use when Christian asks to summarize a day's work, wrap up the day, write a daily summary, or review what was accomplished on a given date. Also trigger for "summarize today", "summarize yesterday", "what did I do today/yesterday", or any request to recap daily progress.
---

# Daily Work Summary

Generate a narrative summary of a day's work and append it to the daily note.

## Step 0: Load the writing style skill

Load the `christian-writing-style` skill before proceeding. The summary must match Christian's voice.

## Step 1: Determine the target date

If the user provided a date as an argument (e.g., `/phd-daily-summary yesterday`, `/phd-daily-summary 2026-03-15`), use that date. Otherwise, ask the user which date to summarize. The default is yesterday.

Date interpretation:

- "today": use the current date
- "yesterday" or no date specified when asked: use the day before the current date
- A specific date like "March 15" or "2026-03-15": use that date

Convert to `YYYY-MM-DD` format. If the date is in the future, tell the user and stop. Confirm with the user before proceeding if there is any ambiguity (e.g., "last Friday" when you're unsure which Friday).

## Step 2: Find the daily note

Daily notes live in `/Users/cgarbin/projects/phd-dissertation-writing/_daily-notes/`. They can be in two locations:

1. Top level: `_daily-notes/YYYY-MM-DD.md`
2. Monthly subdirectory: `_daily-notes/YYYY-MM/YYYY-MM-DD.md`

Check both. If the note doesn't exist, tell the user and stop.

## Step 3: Read the daily note

Read the full daily note. Verify it has a `# Notes` section. If it doesn't, tell the user the note is missing the Notes section and stop (nowhere to insert the summary).

If the Notes section already contains a `## Generated daily summary` sub-section, a summary was already written for this date. Warn the user and ask whether to replace it or skip.

Extract:

- **Pomodoros**: count, task names, categories. Note which tasks had multiple pomodoros (sustained focus).
- **Completed tasks**: lines matching `- [x]` in the Next tasks section.
- **In-progress tasks**: lines matching `- [ ]` that show partial completion (some sub-tasks checked).
- **Notes section**: any existing content (the summary will be appended here).

## Step 4: Gather git commits across all repositories

Read the repository map at `/Users/cgarbin/projects/phd-dissertation-writing/PhD dissertation - temporal EHR summary/Supporting material/Repository map.md` to get the current list of repositories. All repositories live under `~/projects/`. Extract the repository names from the `##` headings (each heading is a repo name, and the path is `~/projects/<heading-name>`).

If fewer than three repositories are found, something is wrong with the repository map or the paths. Stop and tell the user.

For each repo, verify the directory exists on disk before running git log. If a repo directory is missing, warn the user (mention which one) but continue with the remaining repos.

For each repo, run:
```bash
git -C <repo-path> log --after="YYYY-MM-DDT00:00:00" --before="YYYY-MM-DDT23:59:59" --oneline main
```

Collect the commit messages. Skip repos with no commits on that date.

If there are zero commits across all repos AND zero pomodoros in the daily note, there is nothing to summarize. Tell the user and stop.

## Step 5: Write the summary

Write a summary as a bullet list in Christian's writing style (direct, concise, no filler). Each bullet should be a sentence or two covering a coherent group of related work. Don't create one bullet per commit or one per pomodoro. Instead, group related items together so each bullet tells a small story.

The summary should cover:

- What the main focus was (derived from pomodoro tasks and their categories)
- What was accomplished, tying together pomodoro tasks, completed checklist items, and commits into coherent groups
- Which repos saw activity and what kind (new code, refactoring, documentation, infrastructure)
- If tasks were started but not finished, where things stand
- What's queued up next based on incomplete tasks or the Next tasks section, if it exists

Aim for 3-6 bullets. No headers within the summary. No filler phrases like "productive day" or "good progress was made." Do not use semicolons or em-dashes in the summary text.

## Step 6: Append to the daily note

Insert the summary under a `## Generated daily summary` sub-section within the `# Notes` section of the daily note. If the Notes section already has other content, append the new sub-section below it with a blank line separator. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents like `[[CareVue MetaVision decision]]` are fine if relevant.

## Step 7: Confirm

Tell the user the summary was written and show it in the conversation so they can review it without opening the file.
