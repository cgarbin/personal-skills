---
name: close-daily-note
description: Summarize a day's work in a project's daily note and optionally set up the next day's note. Use when Christian says "close the daily note", "wrap up the day", "summarize today/yesterday", "what did I do today", or "set up tomorrow's note", or otherwise asks to recap daily progress or finish the current daily note.
---

# Close Daily Note

Generate a narrative summary of a day's work, insert it at the top of the daily note, and create the next day's note when one doesn't already exist.

This skill works for any project that keeps daily notes in the structured format: a `_daily-notes/` directory, notes named `YYYY-MM-DD Ddd.md`, and `# Pomodoros`, `# Next tasks`, and `# Notes` sections inside each note. It resolves the project from the current session rather than any hardcoded path. If the current location has no such daily notes, it stops (Step 1), which keeps it from firing on free-form journals or non-daily-note projects.

Do not commit any changes. Leave everything for the user to review.

## Fixed section order

Daily notes follow this top-level section order, and the skill produces output that conforms to it:

1. `# Generated daily summary` (added by Step 5, missing until then)
2. `# Pomodoros`
3. `# Next tasks`
4. `# Notes`
5. Free-form sections (any other top-level headings, in the order they appear)

Step 5 inserts the summary at the top of the source note so it is the first thing the user sees. Step 6 builds the next day's note: it emits sections 2-4 in a fixed order whatever order the source used, carries section 3 (Next tasks) and any free-form sections from (5) verbatim, and skips the Notes section's *content*, which is day-specific. The `# Notes` heading itself carries over as an empty stub so the new note's structure is complete from the start.

## Part 1: Generate the daily summary

### Step 1: Gather context

Resolve the user's intent first. No argument or "yesterday" means the day before today. "today" means today. A specific date ("March 15", "2026-03-15") passes through as `YYYY-MM-DD`. If the request is ambiguous ("last Friday" with two plausible Fridays), confirm before proceeding.

One call then resolves the project, the dates, the source note, and the day's commits:

```bash
scripts/context.sh [yesterday|today|YYYY-MM-DD] [project-root]
```

The script lives in the skill directory but finds the project by walking up from the working directory. Run it with the project as the working directory, or pass the project root as the second argument when the session sits somewhere else.

It prints `PROJECT_ROOT`, `DAILY_NOTES_DIR`, `today`, `target`, `now`, `next_day`, `next_dow`, `source_note`, `repo_count`, and one `=== path ===` block per repo that had commits. Substitute these values into later calls as literals, since each Bash invocation is a fresh shell.

Three stops:

- **Exit 1.** No `_daily-notes` directory at or above the working directory, a date the script could not read, a date that does not exist (February 30), or a date in the future. Report what it said. For the missing directory, ask the user to `cd` into the project or name it.
- **Exit 2.** The repository map lists fewer than two repos that exist on disk, so the map or the paths are wrong.
- **Empty `source_note`.** No note exists for that date.

A `MISSING:` line on stderr names a repo listed in the map that is not a git repo on disk. Warn the user about each one and continue with the rest.

Commits come from `git log --branches`, so work on an unmerged feature branch is not silently dropped. De-duplicate any commit that appears on more than one branch.

### Step 2: Read the daily note

Read the full note at `source_note`. Verify it has both a `# Notes` section and a `# Next tasks` section. If `# Notes` is missing, tell the user and stop (a missing Notes section signals this is not a structured project daily note). If `# Next tasks` is missing, tell the user and stop (Step 6 reads from this section, and a missing heading would silently produce an empty carryover). Heading matches are case-insensitive but must be top-level (`# `, not `## `), with optional trailing whitespace allowed.

If the file already contains a top-level `# Generated daily summary` section, a summary was already written for this date. Warn the user and ask whether to replace it or skip.

From the file you just read, extract four signals directly. These feed the Step 3 stop condition and scaffold the Step 4 summary. No shell call: parse the text you already have.

- **Pomodoros**: count of lines under `# Pomodoros` that match the pomodoro template *and have content in the task field*. The template form is `- [ ] 🍅 [task:: ...] [category:: ...] [start:: ...]`. A line counts only when `[task:: ...]` contains at least one non-space, non-`]` character (the empty stub `[task:: ]` does not count). Both checked (`[x]`) and unchecked (`[ ]`) pomodoros count.
- **Done tasks**: lines under `# Next tasks` that are checked off. Match either bullet style: `- [x]` *or* numbered like `1. [x]`, `2. [x]`, with optional leading whitespace for nesting. Capture the full line text.
- **Open tasks**: same as above but `[ ]` instead of `[x]`. Used for scaffolding only, not for the stop condition.
- **Notes lines**: count of non-empty lines under `# Notes` (excluding the heading itself).

Section boundaries are top-level headings (`# `, not `## `) with optional trailing whitespace. Match heading names case-insensitively.

The full Notes content for the Step 4 summary comes straight from the Read output.

### Step 3: Decide whether to continue

Stop only when *all* of the following are true: zero commits from Step 1, zero pomodoros, zero done tasks, and zero notes lines. If any one has content, proceed to Step 4.

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
- What was started but left unfinished within the day's work (a checked subtask under a still-open parent, a commit that landed part of a larger change, a Notes entry that records partial progress).

Do not restate the open task list. The Next tasks section is carried over verbatim into the next day's note in Step 6, so listing queued work in prose duplicates the same information. "In progress" here means partial completion visible in the source, not "everything still on the to-do list."

Use whatever signal is present. Pomodoros, commits, checked tasks, and the Notes section each contribute when available, and the summary gets thinner when fewer of them have content. Resist filling in detail the source does not provide.

When extra signal is present, also note:

- **Pomodoros**: what defined the day's narrative arc, especially tasks with multiple pomodoros (sustained focus).
- **Commits**: what kind of work they represent (new code, refactoring, documentation, infrastructure). When several repos saw activity, note which did what.

Let the day's content set the length. If the day has two stories, write two bullets. If it has five, write five. Stop when you've covered the day honestly. No headers within the summary.

### Step 5: Insert the summary at the top of the daily note

Insert the summary as a top-level `# Generated daily summary` section, placed after the YAML frontmatter and before `# Pomodoros`. The summary is the first thing the user sees when opening the note.

Use Edit with `# Pomodoros` as the anchor. Replace `# Pomodoros` with the new summary block followed by `# Pomodoros`:

```
# Generated daily summary

<bullets from Step 4>

# Pomodoros
```

If a `# Generated daily summary` section already exists (Step 2 detected it and the user chose to replace), remove the old section first with a separate Edit that deletes from `# Generated daily summary` through the blank line before `# Pomodoros`. Do not modify any other section of the note.

Use plain markdown. Wikilinks to existing documents in the same vault are fine if relevant.

## Part 2: Create the next day's note

Runs after Part 1 produces a summary. If Step 3's stop condition halted the run (an empty day with no commits, pomodoros, done tasks, or notes), Part 2 does not run. This supports cascading catch-up across days that have real content: run the skill once per day in sequence and each successful run creates the next day's note. Empty intermediate days trip the stop condition and are skipped, which is correct behavior.

### Step 6: Create the next day's note

```bash
scripts/next-note.sh "<source_note>" "<DAILY_NOTES_DIR>/<next_day> <next_dow>.md" "<now>"
```

Build the destination filename from `next_day` and `next_dow` (both from Step 1), giving `YYYY-MM-DD Ddd.md`. The new note always goes at the top level of `DAILY_NOTES_DIR` even when the source note lived in a `YYYY-MM/` or `YYYY/` archive subdirectory.

The script exits 1 without writing when the destination already exists, when the source has no `# Next tasks` heading, or when the write itself fails. Only a `wrote <path>` line on stdout means a note was created. On the already-exists case, tell the user and skip the rest of Part 2. Skipping forgoes task carryover. The user can merge manually if needed.

The task list is a living document. Tasks that were checked off in the source note stay checked in the carried-over list. Do not remove completed items or modify the list afterward. The user will curate it manually.

## Final report

At the end of the run, tell the user where the summary was written. Do not echo the summary content in the conversation: the user will review it directly in the file. If Part 2 created a new note, add its path and mention that the task list was carried over.
