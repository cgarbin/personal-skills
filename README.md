# Personal Skills

Personal skills for Claude (Cowork and Claude Code), version-controlled and
portable across machines.

## Repository structure

Each skill lives in its own folder under `skills/`, with at least a `SKILL.md`
inside it. The `scripts/` folder contains the install script. Add new skills by
creating a new folder with a `SKILL.md` inside it.

## Setting up a new machine

### 1. Clone the repository

```bash
cd ~/projects
git clone <your-remote-url> personal-skills
```

### 2. Install skills

Run the install script to symlink all skills into the Claude skills directory:

```bash
./scripts/install.sh
```

The script finds every skill under `skills/` and symlinks it into
`~/.claude/skills/`. It is idempotent — re-running it skips skills that are
already linked and picks up any new ones.

If your Claude skills directory is somewhere else, pass it with `--target`:

```bash
./scripts/install.sh --target /path/to/skills
```

With symlinks in place, any edit to the files in this repo (or any `git pull`)
is live immediately — no reinstall step needed.

### Alternative: install from a `.skill` package

If you prefer not to use symlinks (or the skills directory isn't writable),
you can package a skill and install it through the Cowork UI:

```bash
# From a session that has access to the skill-creator
python -m scripts.package_skill ~/projects/personal-skills/skills/<skill-name>
```

This produces a `.skill` file (a zip archive). Install it by double-clicking or
dragging into a Cowork session. The downside is that you need to repackage and
reinstall after every change.

## Day-to-day workflow

1. Edit the skill's `SKILL.md` in this repo.
2. Test it in a Cowork or Claude Code session.
3. Commit when you're happy with the changes.

```bash
git add skills/<skill-name>/SKILL.md
git commit -m "Update <skill-name>: add guidance on X"
git push
```

On other machines, `git pull` picks up the changes. If you used symlinks, the
skill is updated immediately. If you used `.skill` packages, repackage and
reinstall.

## Adding a new skill

```bash
mkdir skills/my-new-skill
# Write the SKILL.md (see official docs for structure and frontmatter format)
# Link the new skill (re-run install — it picks up new skills automatically)
./scripts/install.sh
git add skills/my-new-skill
git commit -m "Add my-new-skill"
```

For skill structure, frontmatter format, and best practices, see the
[official skills documentation](https://agentskills.io/home).
