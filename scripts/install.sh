#!/usr/bin/env bash
# Install personal skills by symlinking them into the Claude skills directory.
#
# Usage:
#   ./scripts/install.sh                      # auto-detect repo path
#   ./scripts/install.sh /path/to/repo        # explicit repo path
#   ./scripts/install.sh --target ~/.claude/skills  # custom target dir
#
# The script finds every skill folder under <repo>/skills/ and creates a
# symlink for it in the target directory (default: ~/.claude/skills).

set -euo pipefail

# ── Parse arguments ──────────────────────────────────────────────────────

REPO_DIR=""
TARGET_DIR="$HOME/.claude/skills"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            TARGET_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [REPO_DIR] [--target SKILLS_DIR]"
            echo ""
            echo "  REPO_DIR    Path to the personal-skills repository."
            echo "              Defaults to the parent directory of this script."
            echo "  --target    Claude skills directory to symlink into."
            echo "              Default: ~/.claude/skills"
            exit 0
            ;;
        *)
            REPO_DIR="$1"
            shift
            ;;
    esac
done

# If no repo dir given, derive it from the script's own location.
if [[ -z "$REPO_DIR" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

SKILLS_SRC="$REPO_DIR/skills"

# ── Validate ─────────────────────────────────────────────────────────────

if [[ ! -d "$SKILLS_SRC" ]]; then
    echo "Error: skills directory not found at $SKILLS_SRC" >&2
    exit 1
fi

# ── Install ──────────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR"

installed=0
skipped=0

for skill_dir in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_dir" ]] || continue

    skill_name="$(basename "$skill_dir")"
    link_path="$TARGET_DIR/$skill_name"

    # Skip if the symlink already points to the right place.
    if [[ -L "$link_path" ]] && [[ "$(readlink "$link_path")" == "$skill_dir" || "$(readlink "$link_path")" == "${skill_dir%/}" ]]; then
        echo "  skip  $skill_name (already linked)"
        skipped=$((skipped + 1))
        continue
    fi

    # Remove a stale symlink (points elsewhere or is broken).
    if [[ -L "$link_path" ]]; then
        echo "  update  $skill_name (re-linking)"
        rm "$link_path"
    elif [[ -e "$link_path" ]]; then
        echo "  skip  $skill_name (non-symlink already exists at $link_path)" >&2
        skipped=$((skipped + 1))
        continue
    fi

    ln -s "$skill_dir" "$link_path"
    echo "  link  $skill_name -> $skill_dir"
    installed=$((installed + 1))
done

echo ""
echo "Done. $installed linked, $skipped skipped."
