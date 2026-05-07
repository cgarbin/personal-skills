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

If your projects live somewhere other than the parent of this repo, pass `--projects-root` so project-scoped skills (see below) land in the right place:

```bash
./scripts/install.sh --projects-root /path/to/projects
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

By default a personal skill is global and gets symlinked into `~/.claude/skills/`, so it loads in every Claude Code session.

## Scoping a skill to a single project

Some skills only make sense inside one project (for example, a skill that knows the layout of a specific dissertation repo). To scope a skill, drop a `SCOPE` file next to its `SKILL.md` containing the project's directory name:

```bash
echo "phd-dissertation" > skills/my-phd-skill/SCOPE
./scripts/install.sh
```

The install script then symlinks the skill into `<projects-root>/phd-dissertation/.claude/skills/my-phd-skill/` instead of the global directory. Claude Code auto-discovers it whenever you start a session in that project.

The projects root defaults to the parent of this repo (so `~/projects/personal-skills` resolves to `~/projects/`). Override it with `--projects-root` on machines where projects live elsewhere. Blank lines and lines starting with `#` are ignored in `SCOPE`, so comments are fine.

If the named project directory does not exist, the script reports a skip and counts it as a conflict so the mistake is visible. Removing the `SCOPE` file (or pointing it at a different project) on the next run cleans up the old symlink.

## Adding an external skill

Add a GitHub URL to `skills.manifest` and re-run the install script:

```bash
echo "https://github.com/<owner>/<repo>/tree/<branch>/<path-to-skill>" >> skills.manifest
./scripts/install.sh
```

External skills are fetched into `from-others/` (git-ignored) and symlinked alongside personal skills. The manifest is committed, so other machines get the same set of external skills after `git pull && ./scripts/install.sh`.

## Tracking external skill changes

The install script maintains a `skills.lock` file that records the commit SHA fetched for each external repo. On subsequent runs, if the upstream repo has new commits, the script shows a full diff of what changed in the skill files before updating. This lets you review upstream changes instead of silently replacing skills.

The lockfile is committed to the repo, so all machines share the same baseline. After reviewing and accepting an update, commit the updated `skills.lock`.

For skill structure, frontmatter format, and best practices, see the [official skills documentation](https://agentskills.io/home).
