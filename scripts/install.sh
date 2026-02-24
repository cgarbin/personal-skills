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
#   3. Symlinks the fetched skills from <repo>/from-others/

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
EXTERNAL_DIR="$REPO_DIR/from-others"
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

    mkdir -p "$EXTERNAL_DIR"

    # Clean out old external skills. The .repos/ cache is kept so we don't
    # re-clone on every run. Everything else is rebuilt from the manifest.
    for old_skill in "$EXTERNAL_DIR"/*/; do
        [[ -d "$old_skill" ]] || continue
        [[ "$(basename "$old_skill")" == ".repos" ]] && continue
        rm -rf "$old_skill"
    done

    # ── Pass 1: group manifest entries by repo ───────────────────────────
    # We collect all paths per repo so we can sparse-checkout only what we
    # need, keeping disk usage low for large repositories.

    declare -A repo_branches   # repo_key -> branch
    declare -A repo_paths      # repo_key -> newline-separated list of paths
    local repo_order=()        # preserve manifest order for output
    declare -A repo_seen

    while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%%#*}"
        line="$(echo "$line" | xargs)"
        [[ -z "$line" ]] && continue

        parse_github_url "$line"
        local repo_key="${GH_OWNER}/${GH_REPO}"

        repo_branches[$repo_key]="$GH_BRANCH"

        if [[ -z "${repo_seen[$repo_key]+x}" ]]; then
            repo_order+=("$repo_key")
            repo_seen[$repo_key]=1
            repo_paths[$repo_key]="$GH_PATH"
        else
            repo_paths[$repo_key]+=$'\n'"$GH_PATH"
        fi
    done < "$MANIFEST"

    # ── Pass 2: clone/update each repo with sparse checkout ──────────────

    for repo_key in "${repo_order[@]}"; do
        local branch="${repo_branches[$repo_key]}"
        local owner="${repo_key%%/*}"
        local repo="${repo_key#*/}"
        local clone_dir="$EXTERNAL_DIR/.repos/${owner}-${repo}"
        local paths="${repo_paths[$repo_key]}"

        if [[ -d "$clone_dir/.git" ]]; then
            echo "  pull      $repo_key"

            # Update sparse-checkout paths (may have changed since last run).
            git -C "$clone_dir" sparse-checkout set --no-cone $paths 2>/dev/null

            git -C "$clone_dir" fetch --quiet --depth 1 origin "$branch" 2>/dev/null \
                && git -C "$clone_dir" reset --quiet --hard "origin/$branch" \
                || true
        else
            echo "  clone     $repo_key (sparse)"
            mkdir -p "$(dirname "$clone_dir")"
            git clone --quiet --depth 1 --branch "$branch" \
                --no-checkout --filter=blob:none \
                "https://github.com/${repo_key}.git" "$clone_dir"

            git -C "$clone_dir" sparse-checkout init
            git -C "$clone_dir" sparse-checkout set --no-cone $paths
            git -C "$clone_dir" checkout --quiet "$branch"
        fi

        # Copy each skill folder into from-others/.
        while IFS= read -r skill_path; do
            [[ -z "$skill_path" ]] && continue
            local skill_name
            skill_name="$(basename "$skill_path")"
            local external_skill_dir="$EXTERNAL_DIR/$skill_name"

            if [[ -d "$clone_dir/$skill_path" ]]; then
                rm -rf "$external_skill_dir"
                cp -R "$clone_dir/$skill_path" "$external_skill_dir"
            else
                echo "  ERROR     $skill_name — path $skill_path not found in $repo_key" >&2
            fi
        done <<< "$paths"
    done

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

# Phase 3: Remove symlinks that point into from-others/ but whose target no
# longer exists (i.e. the skill was removed from the manifest).
for link in "$TARGET_DIR"/*; do
    [[ -L "$link" ]] || continue
    target="$(readlink "$link")"
    case "$target" in
        "$EXTERNAL_DIR"/*)
            if [[ ! -d "$target" ]]; then
                skill_name="$(basename "$link")"
                echo "  remove    $skill_name (no longer in manifest)"
                rm "$link"
            fi
            ;;
    esac
done

# Phase 4: Symlink external skills.
if [[ -d "$EXTERNAL_DIR" ]]; then
    has_external_skills=false
    for skill_dir in "$EXTERNAL_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        skill_name="$(basename "$skill_dir")"
        # Skip the .repos cache directory.
        [[ "$skill_name" == ".repos" ]] && continue
        if [[ "$has_external_skills" == false ]]; then
            echo ""
            echo "External skills:"
            has_external_skills=true
        fi
        symlink_skill "$skill_dir" "$skill_name"
    done
fi

echo ""
echo "Done. $linked linked, $up_to_date already up to date, $conflicts conflicts."
