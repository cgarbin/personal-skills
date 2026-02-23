# Claude Skills

Personal skills for Claude (Cowork / Claude Code).

## Structure

```
skills/
└── christian-writing-style/
    └── SKILL.md
```

Each skill lives in its own folder under `skills/`, mirroring the layout
expected by `.skills/skills/` on each machine.

## Installing a skill on a new machine

Copy (or symlink) the skill folder into your local skills directory:

```bash
cp -r skills/christian-writing-style ~/.skills/skills/
```

The exact path depends on your setup — it's wherever Cowork or Claude Code
looks for skills on that machine.

## Packaging a skill for sharing

From the skill-creator directory:

```bash
python -m scripts.package_skill skills/christian-writing-style
```

This produces a `.skill` file (a zip archive) that can be installed by
double-clicking or dragging into a session.
