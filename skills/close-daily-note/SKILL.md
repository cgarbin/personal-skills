---
name: close-daily-note
description: Summarize a day's work in a project's daily note and optionally set up the next day's note. Use when Christian says "close the daily note", "wrap up the day", "summarize today/yesterday", "what did I do today", or "set up tomorrow's note", or otherwise asks to recap daily progress or finish the current daily note.
---

# Close Daily Note

Generate a narrative summary of a day's work, insert it at the top of the daily note, and create the next day's note when one doesn't already exist.

This skill works for any project that keeps daily notes in the structured format: a `_daily-notes/` directory, notes named `YYYY-MM-DD Ddd.md`, and `# Pomodoros`, `# Next tasks`, and `# Notes` sections inside each note. It resolves the project from the current session rather than any hardcoded path, and works whether or not the project is a git repository. If the current location has no such daily notes, it stops (Step 1), which keeps it from firing on free-form journals or non-daily-note projects.

Do not commit any changes. Leave everything for the user to review.

## What the scripts own

The scripts in `scripts/` do all the deterministic work: date arithmetic, locating the note, collecting commits, counting the day's signals, rewriting sections. Read their output and act on it. Do not re-derive their results by parsing the note yourself, and do not build the next day's note by hand.

Section handling in the next day's note is entirely `next-note.sh`'s job. It emits a fixed order regardless of the order the source used:

1. `# Pomodoros` — rebuilt from the template, carrying the source's `<!-- Categories: -->` comment
2. the day's plan section — heading only, if the source had one
3. `# Next tasks` — carried verbatim
4. `# Notes` — heading only
5. Free-form sections — carried verbatim, in source order

The plan section is any top-level heading starting with "Today", which covers the `# Today`, `# TODAY`, and `# Today's goals` spellings in these notes. Its heading carries over as the user wrote it.

The plan section and `# Notes` keep their heading and lose their content, which belongs to the day that is closing. A free-form section opts into the same reset by putting `<!-- day-specific -->` directly under its heading. Mention that marker if the user asks why a section carried over.

## Part 1: Generate the daily summary

### Step 1: Gather context

Resolve the user's intent first. No argument or "yesterday" means the day before today. "today" means today. A specific date ("March 15", "2026-03-15") passes through as `YYYY-MM-DD`. If the request is ambiguous ("last Friday" with two plausible Fridays), confirm before proceeding.

One call resolves the project, the dates, the source note, the day's commits, and the day's signal counts:

```bash
scripts/context.sh [yesterday|today|YYYY-MM-DD] [project-root]
```

The script lives in the skill directory but finds the project by walking up from the working directory. Run it with the project as the working directory, or pass the project root as the second argument when the session sits somewhere else.

Every `key=value` line prints first, then any `=== label ===` blocks. The keys are `PROJECT_ROOT`, `DAILY_NOTES_DIR`, `today`, `target`, `now`, `next_day`, `next_dow`, `source_note`, `has_summary`, `pomodoros`, `done_tasks`, `open_tasks`, `notes_lines`, `repo_map`, `map_headings`, `map_repos`, `repo_count`. The blocks are one `=== path ===` per repo that had commits, then `=== map unresolved ===`, then `=== done tasks ===` listing the checked-off lines. Substitute the values into later calls as literals, since each Bash invocation is a fresh shell.

Two stops:

- **Exit 1.** No `_daily-notes` directory at or above the working directory, a date the script could not read, a date that does not exist (February 30), or a date in the future. Report what it said. For the missing directory, ask the user to `cd` into the project or name it.
- **Empty `source_note`.** No note exists for that date.

`repo_count=0` is normal for a notes-only project with no repository map. The summary then rests on the note alone.

When a `Repository map.md` is present, judge its resolution rather than trusting a count. A map carries prose sections as well as repo names, so an unresolved `## ` heading is often not a repo at all, and the script reports the names instead of guessing:

- `map_headings > 0` and `map_repos == 0`: the map resolved to nothing. Tell the user which names failed and confirm before continuing, since commits would otherwise be silently absent.
- Some resolved, some not: mention only the unresolved names that look like repo names. Ignore prose headings.

### Step 2: Decide whether to continue

Stop only when *all* of commits, `pomodoros`, `done_tasks`, and `notes_lines` are zero. If any one has content, continue. Checking this before reading the note keeps an empty day cheap.

`open_tasks` is not part of the condition. A note holding only queued work is not a worked day.

### Step 3: Read the daily note

If `has_summary=yes`, a summary was already written for this date. Ask the user whether to replace it or keep it. Keeping it skips Steps 4 and 5 and goes straight to Part 2, which is the useful case when the note was closed but the next day's note was never created. On replace, run this first, before the Read:

```bash
scripts/strip-summary.sh "<source_note>"
```

It exits 0 whether or not the note had a summary, and only touches that section. A non-zero exit means the note was left unchanged: stop and report it.

Then read the full note at `source_note`. The `# Notes` section is the main source for Step 4, and a `# Today` section (or equivalent plan section) shows what the day set out to do, which is how you tell finished work from work that slipped.

Verify the note has both a `# Notes` and a `# Next tasks` top-level heading. If either is missing, tell the user and stop: a missing `# Notes` signals this is not a structured project daily note, and a missing `# Next tasks` would make Step 6 fail after the summary was already written.

### Step 4: Write the summary

Write a summary as a bullet list in Christian's voice. Do not load the `christian-writing-style` skill: a recap of this length does not need the full register guide, and the rules below cover what it does need.

Voice rules for the summary:

- Direct and concrete. Name what was done, not "made progress on" or "worked on." If a task touched Steve's 7/9 presentation, say so. If a commit refactored retrieval, say what changed.
- Past tense, declarative. "Ran the before/after tests." Not "the before/after tests were run" and not "I have been running the tests."
- One coherent group of work per bullet, one or two sentences each. Group by topic, not by source: a bullet can mix a pomodoro, a checked task, and a related commit when they describe the same thread of work.
- No filler. Skip "productive day," "good progress," "made strides," "key takeaways." Do not open a bullet with "continued" or "continued to". Name the concrete action instead ("Ran the before/after tests," not "Continued the test work by running...").
- No metacommentary. Do not write "the day was focused on X." Write what happened.
- No hedging on what the source clearly states. The source is the ground truth for the day.
- US spelling (analyze, behavior, modeling).
- No semicolons as clause-joiners. Use periods.
- No em-dashes. Use periods or parentheses.

The summary should answer:

- What the main focus was.
- What was completed.
- What was started but left unfinished within the day's work (a checked subtask under a still-open parent, a commit that landed part of a larger change, a Notes entry that records partial progress, a plan item the day never reached).

Do not restate the open task list. Step 6 carries `# Next tasks` verbatim into the next day's note, so listing queued work in prose duplicates it. "In progress" here means partial completion visible in the source, not "everything still on the to-do list."

Use whatever signal is present. Pomodoros, commits, checked tasks, and the Notes section each contribute when available, and the summary gets thinner when fewer of them have content. Resist filling in detail the source does not provide.

When extra signal is present, also note:

- **Pomodoros**: what defined the day's narrative arc, especially tasks with multiple pomodoros (sustained focus).
- **Commits**: what kind of work they represent (new code, refactoring, documentation, infrastructure). When several repos saw activity, note which did what. Commits come from `git log --branches`, so work on an unmerged feature branch is not silently dropped. De-duplicate any commit that appears on more than one branch.

Let the day's content set the length. If the day has two stories, write two bullets. If it has five, write five. Stop when you've covered the day honestly. No headers within the summary.

### Step 5: Insert the summary at the top of the daily note

Insert the summary as a top-level `# Generated daily summary` section, placed after the YAML frontmatter and before `# Pomodoros`, so it is the first thing the user sees when opening the note.

Use Edit with `# Pomodoros` as the anchor, replacing it with:

```
# Generated daily summary

<bullets from Step 4>

# Pomodoros
```

Because Step 3 already stripped any earlier summary, this is the same single Edit on a first run and on a re-run. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents in the same vault are fine if relevant.

## Part 2: Create the next day's note

Runs once Part 1 has left a summary in place, whether this run wrote it or the user chose to keep an existing one. If Step 2's stop condition halted the run, Part 2 does not run. This supports cascading catch-up: run the skill once per day in sequence and each successful run creates the next day's note. Empty intermediate days trip the stop condition and are skipped, which is correct.

### Step 6: Create the next day's note

```bash
scripts/next-note.sh "<source_note>" "<DAILY_NOTES_DIR>/<next_day> <next_dow>.md" "<now>"
```

Build the destination filename from `next_day` and `next_dow` (both from Step 1), giving `YYYY-MM-DD Ddd.md`. The new note always goes at the top level of `DAILY_NOTES_DIR` even when the source note lived in an archive subdirectory.

The script exits 1 without writing when the destination already exists, when the source has no `# Next tasks` heading, or when the write itself fails. Only a `wrote <path>` line on stdout means a note was created. On the already-exists case, tell the user and skip the rest of Part 2. Skipping forgoes task carryover. The user can merge manually if needed.

The task list is a living document. Tasks that were checked off in the source note stay checked in the carried-over list. Do not remove completed items or modify the list afterward. The user will curate it manually.

## Final report

Tell the user where the summary was written. Do not echo the summary content in the conversation: the user will review it directly in the file. If Part 2 created a new note, add its path and mention that the task list was carried over. Note anything that limited the summary, such as `repo_count=0` meaning no commit signal was available.
