# Personal Skills

Personal skills, mostly for writing. Use at your own risk.

- [Set up a new machine](#set-up-a-new-machine)
- [Update a skill](#update-a-skill)
- [Add a new personal skill](#add-a-new-personal-skill)
- [Install skills in specific repos](#install-skills-in-specific-repos)
- [Evaluate a skill](#evaluate-a-skill)
- [Add an external skill](#add-an-external-skill)
- [Track external skill changes](#track-external-skill-changes)

The text refers to "Claude" and "CLAUDE.md", but should be generalizable to any agent that can load skills from a folder.

External skills I use are listed in `skills.manifest`. The install script fetches them and symlinks them into `~/.claude/skills/` alongside personal skills.

- **[christian-writing-style](skills/christian-writing-style/)**: the writing rules for anything under my name, from a technical article to a commit subject line.
- **[text-review](skills/text-review/)**: reviews writing for accuracy, organization, and clarity. Presents findings by severity and waits before editing.
- **[code-comments](skills/code-comments/)**: Rules to write useful comments and docstrings. It works together with `christian-writing-style`.
- **[commit](skills/commit/)**: commits the session's changes in logical groups, with a review step before each commit.
- **[python-dev-process](skills/python-dev-process/)** (opt-in): my Python process, covering project phases, tooling, testing, and refactoring discipline.

## Set up a new machine

### 1. Clone the repository

```bash
cd ~/projects
git clone <your-remote-url> personal-skills
```

### 2. Install skills

Run the install script to symlink your skills into the Claude skills directory:

```bash
./scripts/install.sh
```

The script fetches external skills listed in `skills.manifest`, then symlinks both personal and external skills into `~/.claude/skills/`. Running it again is safe. A re-run:

- updates external skills
- leaves alone the ones already linked
- picks up new ones
- removes a symlink when its skill was deleted, lost its `SKILL.md`, or became opt-in
- skips folders that hold no `SKILL.md`

The closing line counts what it linked, what was already current, what it removed, and what it could not touch.

If your Claude skills directory is somewhere else, pass it with `--target`:

```bash
./scripts/install.sh --target /path/to/skills
```

With symlinks in place, any edit to the files in this repo (or any `git pull`) is live immediately. No reinstall step needed.

### 3. Configure Claude Code permissions

The `configure-permissions.sh` script manages the allow/deny permission lists in Claude Code settings files. It merges a set of desired permissions into the file, reports what was added, and lists any extra permissions not in the desired set so you can choose to remove them.

```bash
# Global settings (~/.claude/settings.json)
./scripts/configure-permissions.sh --global

# Project settings (.claude/settings.local.json in current directory)
./scripts/configure-permissions.sh --project

# Project settings in a specific directory
./scripts/configure-permissions.sh --project /path/to/project
```

The desired allow/deny lists are defined at the top of the script. Edit them to change your defaults.

## Update a skill

1. Edit the skill's `SKILL.md` in this repo.
2. Test it in a Cowork or Claude Code session. For a change worth measuring, see [Evaluate a skill](#evaluate-a-skill).
3. Commit when you're happy with the changes.

```bash
git add skills/<skill-name>/SKILL.md
git commit -m "Update <skill-name>: add guidance on X"
git push
```

On other machines, `git pull` picks up the changes.

## Add a new personal skill

```bash
mkdir skills/my-new-skill
# Write the SKILL.md (see official docs for structure and frontmatter format)
./scripts/install.sh
git add skills/my-new-skill
git commit -m "Add my-new-skill"
```

By default a personal skill is global and gets symlinked into `~/.claude/skills/`, so it loads in every Claude Code session.

The folder needs a `SKILL.md` to count as a skill. Without one, install prints `skip <name> (no SKILL.md)` and links nothing.

## Install skills in specific repos

Some skills should not load in every session to save tokens. To mark a skill as repo-specific, add an empty `OPTIN` file next to its `SKILL.md`:

```bash
touch skills/my-narrow-skill/OPTIN
./scripts/install.sh
```

The next install run skips the skill (and removes any existing global symlink to it). Install it in specific repos with `--link-into`:

```bash
./scripts/install.sh --link-into /path/to/repo/.claude/skills my-narrow-skill
```

The path must end in `.claude/skills` (same format as `--target`). The script creates the directory if missing and symlinks `my-narrow-skill` inside it.

Repeat on all machines where you want the skill active.

## Evaluate a skill

A skill can fail in two independent ways. It can fail to trigger when it should, or it can trigger and then apply its rules badly.

Eval files live in `skills/<skill-name>-workspace/`, a sibling of the skill. Inputs are committed and run outputs are gitignored.

```text
skills/<skill-name>-workspace/
  trigger-eval.json       # does the skill trigger? committed
  evals/evals.json        # does it behave? committed
  evals/fixtures/         # files the behavioral evals work on, committed
  iteration-N/            # run outputs, ignored
  trigger-<variant>.json  # run outputs, ignored
```

### Does the skill trigger?

`trigger-eval.json` is a list of realistic queries a user would type, each labeled with whether the skill should trigger. Aim for ten of each label, and write negatives that share vocabulary with the skill and should not trigger it, rather than obviously unrelated requests.

```bash
./scripts/trigger-eval.py <skill-name> skills/<skill-name>-workspace/trigger-eval.json 5
```

Each query runs `claude -p` against the installed skill, so other skills compete for it the same way they do in a real session. The output reports a trigger rate per query and names the other skills that fired.

Use at least five runs per query. At three, a query at 0.33 versus 0.67 is one run flipping results. That noise is easy to mistake for a real regression.

To compare candidate descriptions, pass `--description`. The variant is written into the skill for the length of the run and restored afterward, because `claude -p` reads the skill from disk. Run variants one at a time, since they share that file. `skills/christian-writing-style-workspace/compare-descriptions.sh` shows an example.

Keep the skill description concise. It is loaded into the coding agent's context in every session. A long one costs tokens whether or not the skill triggers.

**Do not use skill-creator's `scripts/run_eval.py`.** It registers the skill under test by writing `.claude/commands/<name>.md`, which Claude Code shows as a slash command. The model only runs one of those when the user types its name, so a bare task prompt never triggers one and every description scores 0.0 regardless of quality.

### Does the skill behave correctly?

`evals/evals.json` holds task prompts with assertions, and `evals/fixtures/` holds the files those prompts work on. Run each prompt as a subagent, then check the assertions against what it produced.

- **Write assertions a single run either satisfies or does not.** Grade mechanically where you can, comparing tokenized source rather than eyeballing a diff.
- **Plant something in the input file that has to survive.** An agent that deletes everything passes every "removes X" assertion. Without one, the eval scores that run as a success.
- **Keep the input file otherwise correct.** Bugs unrelated to what you are testing pull the agent toward them, and every future round rediscovers the same ones.

### When to stop iterating

Some work will not trigger a skill however its description is worded. Rewriting a description moves the queries that were already close and leaves the rest at zero.

Two signs the description is not the problem:

- Two differently worded descriptions fail the same queries.
- Trigger rates sit at 0 or 1 with nothing in between. A rate in the middle means wording still has room to move it.

A line in `claude-md/CLAUDE.md` naming the skill looks like a way around this, since that file is in context for every session. Tested on one skill, it changed nothing. The queries that scored zero still scored zero with the line in place, and the work produced with it was no better and carried about twice the commentary. Treat the queries you cannot reach as out of reach.

## Add an external skill

Add a GitHub URL to `skills.manifest` and re-run the install script:

```bash
echo "https://github.com/<owner>/<repo>/tree/<branch>/<path-to-skill>" >> skills.manifest
./scripts/install.sh
```

External skills are fetched into `from-others/` (git-ignored) and symlinked alongside personal skills. The manifest is committed, so other machines get the same set of external skills after `git pull && ./scripts/install.sh`.

## Track external skill changes

The install script maintains a `skills.lock` file that records the commit SHA fetched for each external repo. On subsequent runs, if the upstream repo has new commits, the script shows a full diff of what changed in the skill files before updating. This lets you review upstream changes instead of silently replacing skills.

The lockfile is committed to the repo, so all machines share the same baseline. After reviewing and accepting an update, commit the updated `skills.lock`.

For skill structure, frontmatter format, and best practices, see the [official skills documentation](https://agentskills.io/home).
