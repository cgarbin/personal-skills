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

linked=0
up_to_date=0
conflicts=0

for skill_dir in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_dir" ]] || continue

    skill_name="$(basename "$skill_dir")"
    link_path="$TARGET_DIR/$skill_name"

    # Already points to the right place — nothing to do.
    if [[ -L "$link_path" ]] && [[ "$(readlink "$link_path")" == "$skill_dir" || "$(readlink "$link_path")" == "${skill_dir%/}" ]]; then
        echo "  ok      $skill_name (already linked)"
        up_to_date=$((up_to_date + 1))
        continue
    fi

    # Stale symlink (points elsewhere or is broken) — safe to replace.
    if [[ -L "$link_path" ]]; then
        echo "  update  $skill_name (re-linking)"
        rm "$link_path"
    elif [[ -e "$link_path" ]]; then
        echo "  CONFLICT  $skill_name — a file or folder already exists at $link_path" >&2
        echo "            Remove or rename it, then re-run this script." >&2
        conflicts=$((conflicts + 1))
        continue
    fi

    ln -s "$skill_dir" "$link_path"
    echo "  link    $skill_name -> $skill_dir"
    linked=$((linked + 1))
done

echo ""
echo "Done. $linked linked, $up_to_date already up to date, $conflicts conflicts."
