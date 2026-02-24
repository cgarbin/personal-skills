#!/usr/bin/env bash
# Install personal and external skills by symlinking them into the Claude
# skills directory.
#
# Usage:
#   ./scripts/install.sh                      # auto-detect repo path
#   ./scripts/install.sh /path/to/repo        # explicit repo path
#   ./scripts/install.sh --target ~/.claude/skills  # custom target dir
#
# The script:
#   1. Symlinks every personal skill from <repo>/skills/
#   2. Fetches external skills listed in skills.manifest (if present)
#   3. Symlinks the fetched skills from <repo>/vendor/

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
VENDOR_DIR="$REPO_DIR/vendor"
MANIFEST="$REPO_DIR/skills.manifest"

# ── Validate ─────────────────────────────────────────────────────────────

if [[ ! -d "$SKILLS_SRC" ]]; then
    echo "Error: skills directory not found at $SKILLS_SRC" >&2
    exit 1
fi

# ── Helpers ──────────────────────────────────────────────────────────────

linked=0
up_to_date=0
conflicts=0

# symlink_skill <source_dir> <skill_name>
#   Creates a symlink in TARGET_DIR, handling duplicates and conflicts.
symlink_skill() {
    local src="$1"
    local skill_name="$2"
    local link_path="$TARGET_DIR/$skill_name"

    # Already points to the right place — nothing to do.
    if [[ -L "$link_path" ]] && [[ "$(readlink "$link_path")" == "$src" || "$(readlink "$link_path")" == "${src%/}" ]]; then
        echo "  ok        $skill_name (already linked)"
        up_to_date=$((up_to_date + 1))
        return
    fi

    # Stale symlink (points elsewhere or is broken) — safe to replace.
    if [[ -L "$link_path" ]]; then
        echo "  update    $skill_name (re-linking)"
        rm "$link_path"
    elif [[ -e "$link_path" ]]; then
        echo "  CONFLICT  $skill_name — a file or folder already exists at $link_path" >&2
        echo "            Remove or rename it, then re-run this script." >&2
        conflicts=$((conflicts + 1))
        return
    fi

    ln -s "$src" "$link_path"
    echo "  link      $skill_name -> $src"
    linked=$((linked + 1))
}

# parse_github_url <url>
#   Extracts owner, repo, branch, and path from a GitHub tree URL.
#   Sets: GH_OWNER, GH_REPO, GH_BRANCH, GH_PATH
parse_github_url() {
    local url="$1"
    # Expected: https://github.com/<owner>/<repo>/tree/<branch>/<path>
    local stripped="${url#https://github.com/}"
    GH_OWNER="${stripped%%/*}"
    stripped="${stripped#*/}"
    GH_REPO="${stripped%%/*}"
    stripped="${stripped#*/tree/}"
    GH_BRANCH="${stripped%%/*}"
    GH_PATH="${stripped#*/}"
}

# ── Fetch external skills from manifest ──────────────────────────────────

fetch_external_skills() {
    if [[ ! -f "$MANIFEST" ]]; then
        return
    fi

    echo "Fetching external skills..."
    echo ""

    mkdir -p "$VENDOR_DIR"

    # Track which repos we've already cloned/updated this run.
    declare -A fetched_repos

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip blank lines and comments.
        line="${line%%#*}"
        line="$(echo "$line" | xargs)"
        [[ -z "$line" ]] && continue

        parse_github_url "$line"

        local repo_key="${GH_OWNER}/${GH_REPO}"
        local clone_dir="$VENDOR_DIR/.repos/${GH_OWNER}-${GH_REPO}"

        # Clone or update the repo (once per repo per run).
        if [[ -z "${fetched_repos[$repo_key]+x}" ]]; then
            if [[ -d "$clone_dir/.git" ]]; then
                echo "  pull      $repo_key"
                git -C "$clone_dir" fetch --quiet --depth 1 origin "$GH_BRANCH" 2>/dev/null \
                    && git -C "$clone_dir" reset --quiet --hard "origin/$GH_BRANCH" \
                    || true
            else
                echo "  clone     $repo_key"
                mkdir -p "$(dirname "$clone_dir")"
                git clone --quiet --depth 1 --branch "$GH_BRANCH" \
                    "https://github.com/${repo_key}.git" "$clone_dir"
            fi
            fetched_repos[$repo_key]=1
        fi

        # Copy the skill folder into vendor/ so the symlink target is stable.
        local skill_name
        skill_name="$(basename "$GH_PATH")"
        local vendor_skill_dir="$VENDOR_DIR/$skill_name"

        if [[ -d "$clone_dir/$GH_PATH" ]]; then
            rm -rf "$vendor_skill_dir"
            cp -R "$clone_dir/$GH_PATH" "$vendor_skill_dir"
        else
            echo "  ERROR     $skill_name — path $GH_PATH not found in $repo_key" >&2
            continue
        fi
    done < "$MANIFEST"

    echo ""
}

# ── Install ──────────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR"

# Phase 1: Fetch external skills (if manifest exists).
fetch_external_skills

# Phase 2: Symlink personal skills.
echo "Personal skills:"
for skill_dir in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_dir" ]] || continue
    symlink_skill "$skill_dir" "$(basename "$skill_dir")"
done

# Phase 3: Symlink external (vendor) skills.
if [[ -d "$VENDOR_DIR" ]]; then
    has_vendor_skills=false
    for skill_dir in "$VENDOR_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        # Skip the .repos cache directory.
        [[ "$skill_name" == ".repos" ]] && continue
        if [[ "$has_vendor_skills" == false ]]; then
            echo ""
            echo "External skills:"
            has_vendor_skills=true
        fi
        symlink_skill "$skill_dir" "$skill_name"
    done
fi

echo ""
echo "Done. $linked linked, $up_to_date already up to date, $conflicts conflicts."
