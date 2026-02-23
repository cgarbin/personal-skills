# Personal Skills

Personal skills for Claude (Cowork and Claude Code), version-controlled and
portable across machines.

## Repository structure

```
skills/
└── christian-writing-style/
    └── SKILL.md
```

Each skill lives in its own folder under `skills/`. Add new skills by creating
a new folder with a `SKILL.md` inside it.

## Setting up a new machine

### 1. Clone the repository

```bash
cd ~/projects
git clone <your-remote-url> personal-skills
```

### 2. Symlink skills into the Claude skills directory

Cowork and Claude Code look for skills in `~/.claude/skills/`. Symlink each
skill from this repo so that changes are picked up immediately:

```bash
# Create the target directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink each skill
ln -s ~/projects/personal-skills/skills/christian-writing-style \
      ~/.claude/skills/christian-writing-style
```

With symlinks in place, any edit to the files in this repo (or any `git pull`)
is live immediately — no reinstall step needed.

If the symlink path doesn't work (the skills directory location can vary by
platform and version), check where your existing skills are stored:

```bash
find ~ -path "*/.claude/skills" -o -path "*/.skills/skills" 2>/dev/null
```

Then adjust the symlink target accordingly.

### Alternative: install from a `.skill` package

If you prefer not to use symlinks (or the skills directory isn't writable),
you can package a skill and install it through the Cowork UI:

```bash
# From a session that has access to the skill-creator
python -m scripts.package_skill ~/projects/personal-skills/skills/christian-writing-style
```

This produces a `christian-writing-style.skill` file (a zip archive). Install
it by double-clicking or dragging into a Cowork session. The downside is that
you need to repackage and reinstall after every change.

## Day-to-day workflow

1. Edit the skill's `SKILL.md` in this repo.
2. Test it in a Cowork or Claude Code session.
3. Commit when you're happy with the changes.

```bash
git add skills/christian-writing-style/SKILL.md
git commit -m "Update writing style: add guidance on X"
git push
```

On other machines, `git pull` picks up the changes. If you used symlinks, the
skill is updated immediately. If you used `.skill` packages, repackage and
reinstall.

## Adding a new skill

```bash
mkdir skills/my-new-skill
# Write the SKILL.md (see official docs for structure and frontmatter format)
# Symlink it (or package and install)
ln -s ~/projects/personal-skills/skills/my-new-skill ~/.claude/skills/my-new-skill
git add skills/my-new-skill
git commit -m "Add my-new-skill"
```

For skill structure, frontmatter format, and best practices, see the
[official skills documentation](https://agentskills.io/home).
