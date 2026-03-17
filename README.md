# Personal Skills

Personal skills for Claude (Cowork and Claude Code), version-controlled and portable across machines.

## Repository structure

Personal skills live under `skills/`, each in its own folder with a `SKILL.md`. External skills from GitHub are listed in `skills.manifest` and fetched into `from-others/` at install time. The `scripts/` folder contains the install script.

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

The script fetches external skills listed in `skills.manifest`, then symlinks both personal and external skills into `~/.claude/skills/`. It is idempotent — re-running it updates external skills, skips personal skills that are already linked, and picks up any new ones.

If your Claude skills directory is somewhere else, pass it with `--target`:

```bash
./scripts/install.sh --target /path/to/skills
```

With symlinks in place, any edit to the files in this repo (or any `git pull`) is live immediately — no reinstall step needed.

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

## Day-to-day workflow

1. Edit the skill's `SKILL.md` in this repo.
2. Test it in a Cowork or Claude Code session.
3. Commit when you're happy with the changes.

```bash
git add skills/<skill-name>/SKILL.md
git commit -m "Update <skill-name>: add guidance on X"
git push
```

On other machines, `git pull` picks up the changes. If you used symlinks, the skill is updated immediately. If you used `.skill` packages, repackage and reinstall.

## Adding a personal skill

```bash
mkdir skills/my-new-skill
# Write the SKILL.md (see official docs for structure and frontmatter format)
./scripts/install.sh
git add skills/my-new-skill
git commit -m "Add my-new-skill"
```

## Adding an external skill

Add a GitHub URL to `skills.manifest` and re-run the install script:

```bash
echo "https://github.com/<owner>/<repo>/tree/<branch>/<path-to-skill>" >> skills.manifest
./scripts/install.sh
```

External skills are fetched into `from-others/` (git-ignored) and symlinked alongside personal skills. The manifest is committed, so other machines get the same set of external skills after `git pull && ./scripts/install.sh`.

For skill structure, frontmatter format, and best practices, see the [official skills documentation](https://agentskills.io/home).
