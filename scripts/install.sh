#!/usr/bin/env bash
# Install personal and external skills by symlinking them into the Claude
# skills directory, and symlink the global CLAUDE.md into ~/.claude/.
#
# Usage:
#   ./scripts/install.sh                                 # repo = parent of this script's dir
#   ./scripts/install.sh /path/to/repo                   # explicit repo path
#   ./scripts/install.sh --target ~/.claude/skills       # custom target dir
#   ./scripts/install.sh --link-into <path> <skill>     # opt-in per repo
#
# Personal skills default to global (symlinked into TARGET_DIR). A skill
# becomes opt-in by placing an empty OPTIN file next to its SKILL.md.
# Opt-in skills are skipped by the normal install pass and must be
# installed per repo with --link-into.
#
# The script:
#   1. Symlinks the global CLAUDE.md from <repo>/claude-md/
#   2. Cleans up stale personal skill symlinks (deleted, or now opt-in)
#   3. Symlinks non-opt-in personal skills from <repo>/skills/ globally
#   4. Fetches external skills listed in skills.manifest (if present)
#   5. Cleans up stale external symlinks
#   6. Symlinks external skills from <repo>/from-others/

set -euo pipefail

# ── Parse arguments ──────────────────────────────────────────────────────

REPO_DIR=""
TARGET_DIR="$HOME/.claude/skills"
LINK_INTO_PATH=""
LINK_INTO_SKILL=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            if [[ $# -lt 2 ]]; then
                echo "Error: --target requires a value." >&2
                exit 1
            fi
            TARGET_DIR="$2"
            shift 2
            ;;
        --link-into)
            if [[ $# -lt 3 ]]; then
                echo "Error: --link-into requires <project-path> <skill-name>." >&2
                exit 1
            fi
            LINK_INTO_PATH="$2"
            LINK_INTO_SKILL="$3"
            shift 3
            ;;
        -h|--help)
            echo "Usage: $0 [REPO_DIR] [--target SKILLS_DIR]"
            echo "       $0 --link-into <project-path> <skill-name>"
            echo ""
            echo "  REPO_DIR       Path to the personal-skills repository."
            echo "                 Defaults to the parent of the directory holding"
            echo "                 this script."
            echo "  --target       Claude skills directory to symlink into."
            echo "                 Default: ~/.claude/skills"
            echo "  --link-into    One-shot: symlink <skill-name> into"
            echo "                 <project-path>/.claude/skills/ and exit. Use"
            echo "                 for skills marked opt-in (with an OPTIN file)."
            echo "                 The symlink survives later runs of the script."
            exit 0
            ;;
        --*)
            echo "Error: unknown option $1" >&2
            exit 1
            ;;
        *)
            REPO_DIR="$1"
            shift
            ;;
    esac
done

# If no repo dir given, use the parent of this script's directory as the
# base path. The script lives at <repo>/scripts/install.sh, so its parent
# directory is the repo root.
if [[ -z "$REPO_DIR" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

SKILLS_SRC="$REPO_DIR/skills"
EXTERNAL_DIR="$REPO_DIR/from-others"
MANIFEST="$REPO_DIR/skills.manifest"
LOCKFILE="$REPO_DIR/skills.lock"
CLAUDE_MD_SRC="$REPO_DIR/claude-md/CLAUDE.md"
CLAUDE_MD_TARGET="$HOME/.claude/CLAUDE.md"
OPTIN_FILENAME="OPTIN"

if [[ ! -d "$SKILLS_SRC" ]]; then
    echo "Error: skills directory not found at $SKILLS_SRC" >&2
    exit 1
fi

# ── Counters ─────────────────────────────────────────────────────────────

linked=0
up_to_date=0
conflicts=0

# ── Symlink helpers ──────────────────────────────────────────────────────

# ensure_symlink <source> <link_path> <display_name>
#   Creates or updates a symlink. Handles three cases:
#   - Already linked correctly → report "ok"
#   - Stale or broken symlink → replace it
#   - Non-symlink exists at the path → report conflict, don't touch it
ensure_symlink() {
    local src="$1"
    local link_path="$2"
    local display_name="$3"

    # Compare with and without trailing slash because glob expansion adds one.
    if [[ -L "$link_path" ]] && [[ "$(readlink "$link_path")" == "$src" || "$(readlink "$link_path")" == "${src%/}" ]]; then
        echo "  ok        $display_name (already linked)"
        up_to_date=$((up_to_date + 1))
        return
    fi

    # Stale symlink (points elsewhere or is broken) — safe to replace.
    if [[ -L "$link_path" ]]; then
        echo "  update    $display_name (re-linking)"
        rm "$link_path"
    # Non-symlink file or folder — don't touch it.
    elif [[ -e "$link_path" ]]; then
        echo "  CONFLICT  $display_name — a file or folder already exists at $link_path" >&2
        echo "            Remove or rename it, then re-run this script." >&2
        conflicts=$((conflicts + 1))
        return
    fi

    ln -s "$src" "$link_path"
    echo "  link      $display_name -> $src"
    linked=$((linked + 1))
}

# symlink_skill <source_dir> <skill_name>
#   Convenience wrapper: symlinks a skill into TARGET_DIR.
symlink_skill() {
    ensure_symlink "$1" "$TARGET_DIR/$2" "$2"
}

# remove_stale_external_symlinks
#   Removes symlinks in TARGET_DIR that point into EXTERNAL_DIR but whose
#   target no longer exists (i.e. the skill was removed from the manifest).
remove_stale_external_symlinks() {
    for link in "$TARGET_DIR"/*; do
        # Only inspect symlinks; skip regular files and folders.
        [[ -L "$link" ]] || continue
        local target
        target="$(readlink "$link")"
        case "$target" in
            "$EXTERNAL_DIR"/*)
                if [[ ! -d "$target" ]]; then
                    echo "  remove    $(basename "$link") (no longer in manifest)"
                    rm "$link"
                fi
                ;;
        esac
    done
}

# ── Lockfile helpers ──────────────────────────────────────────────────

# read_locked_sha <repo_key>
#   Prints the locked SHA for the given repo, or empty string if not found.
read_locked_sha() {
    local repo_key="$1"
    if [[ -f "$LOCKFILE" ]]; then
        awk -v key="$repo_key" '$1 == key { print $2 }' "$LOCKFILE"
    fi
}

# write_locked_sha <repo_key> <sha>
#   Upserts the SHA for repo_key in the lockfile, keeping it sorted.
write_locked_sha() {
    local repo_key="$1"
    local sha="$2"

    if [[ -f "$LOCKFILE" ]] && grep -q "^${repo_key} " "$LOCKFILE"; then
        sed -i '' "s|^${repo_key} .*|${repo_key} ${sha}|" "$LOCKFILE"
    else
        echo "${repo_key} ${sha}" >> "$LOCKFILE"
    fi

    sort -o "$LOCKFILE" "$LOCKFILE"
}

# show_changelog <clone_dir> <repo_key> <old_sha> <new_sha> <paths>
#   Shows the diff of the skill files between the old and new SHAs.
#   Prints nothing if the skill files themselves did not change (the repo
#   may have other commits that don't affect the skills we use).
#   Returns 0 if skill files changed, 1 if not.
show_changelog() {
    local clone_dir="$1"
    local repo_key="$2"
    local old_sha="$3"
    local new_sha="$4"
    local paths="$5"

    local diff_output
    # shellcheck disable=SC2086
    diff_output="$(git -C "$clone_dir" diff "${old_sha}" "${new_sha}" -- $paths 2>/dev/null)" || true

    if [[ -z "$diff_output" ]]; then
        return 1
    fi

    echo ""
    echo "  ── Changes in $repo_key (${old_sha:0:12} -> ${new_sha:0:12}) ──"
    echo ""
    echo "$diff_output"
    echo ""
    return 0
}

# ── CLAUDE.md ──────────────────────────────────────────────────────────

# install_claude_md
#   Symlinks <repo>/claude-md/CLAUDE.md → CLAUDE_MD_TARGET.
#   Skips if claude-md/CLAUDE.md doesn't exist in the repo.
install_claude_md() {
    [[ -f "$CLAUDE_MD_SRC" ]] || return

    mkdir -p "$(dirname "$CLAUDE_MD_TARGET")"
    echo "CLAUDE.md:"
    ensure_symlink "$CLAUDE_MD_SRC" "$CLAUDE_MD_TARGET" "CLAUDE.md"
}

# ── GitHub URL parsing ───────────────────────────────────────────────────

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

# ── External skill fetching ─────────────────────────────────────────────

# clean_external_skills
#   Removes previously fetched skill folders (but keeps the .repos/ cache).
clean_external_skills() {
    for old_skill in "$EXTERNAL_DIR"/*/; do
        [[ -d "$old_skill" ]] || continue
        [[ "$(basename "$old_skill")" == ".repos" ]] && continue
        rm -rf "$old_skill"
    done
}

# parse_manifest
#   Reads skills.manifest into the manifest_entries array.
#   Each element is "owner/repo|branch|path".
parse_manifest() {
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Strip comments and whitespace.
        line="${line%%#*}"
        line="$(echo "$line" | xargs)"
        [[ -z "$line" ]] && continue

        parse_github_url "$line"
        manifest_entries+=("${GH_OWNER}/${GH_REPO}|${GH_BRANCH}|${GH_PATH}")
    done < "$MANIFEST"
}

# collect_paths_for_repo <repo_key>
#   Scans manifest_entries and prints all paths for the given repo,
#   one per line.
collect_paths_for_repo() {
    local target_repo="$1"
    for entry in "${manifest_entries[@]}"; do
        local repo="${entry%%|*}"
        if [[ "$repo" == "$target_repo" ]]; then
            # Strip "owner/repo|branch|" to get the path.
            echo "${entry##*|}"
        fi
    done
}

# clone_or_update_repo <repo_key> <branch> <clone_dir> <paths>
#   Sparse-clones or updates a GitHub repo, checking out only the given paths.
clone_or_update_repo() {
    local repo_key="$1"
    local branch="$2"
    local clone_dir="$3"
    local paths="$4"

    if [[ -d "$clone_dir/.git" ]]; then
        echo "  pull      $repo_key"
        # Intentional word-splitting: sparse-checkout needs separate args.
        # shellcheck disable=SC2086
        git -C "$clone_dir" sparse-checkout set --no-cone $paths 2>/dev/null
        git -C "$clone_dir" fetch --quiet origin "$branch" 2>/dev/null \
            && git -C "$clone_dir" reset --quiet --hard "origin/$branch" \
            || true
    else
        echo "  clone     $repo_key (sparse)"
        mkdir -p "$(dirname "$clone_dir")"
        git clone --quiet --branch "$branch" \
            --no-checkout --sparse \
            "https://github.com/${repo_key}.git" "$clone_dir"
        # shellcheck disable=SC2086
        git -C "$clone_dir" sparse-checkout set --no-cone $paths
        git -C "$clone_dir" checkout --quiet "$branch"
    fi
}

# copy_skills_from_repo <clone_dir> <paths>
#   Copies each skill folder from a cloned repo into EXTERNAL_DIR.
copy_skills_from_repo() {
    local clone_dir="$1"
    local paths="$2"

    while IFS= read -r skill_path; do
        [[ -z "$skill_path" ]] && continue
        local skill_name
        skill_name="$(basename "$skill_path")"

        if [[ -d "$clone_dir/$skill_path" ]]; then
            rm -rf "${EXTERNAL_DIR:?}/$skill_name"
            cp -R "$clone_dir/$skill_path" "$EXTERNAL_DIR/$skill_name"
        else
            echo "  ERROR     $skill_name — path $skill_path not found" >&2
        fi
    done <<< "$paths"
}

# fetch_external_skills
#   Reads the manifest, clones/updates repos, and copies skill folders.
fetch_external_skills() {
    [[ -f "$MANIFEST" ]] || return

    echo "Fetching external skills..."
    echo ""

    mkdir -p "$EXTERNAL_DIR"
    clean_external_skills

    manifest_entries=()
    parse_manifest

    # Deduplicate repos so we clone each once. Uses string matching because
    # macOS ships bash 3.2, which lacks associative arrays.
    local processed_repos=""
    for entry in "${manifest_entries[@]}"; do
        local repo_key="${entry%%|*}"

        # Skip repos we've already handled.
        if [[ "$processed_repos" == *"|${repo_key}|"* ]]; then
            continue
        fi
        processed_repos="${processed_repos}|${repo_key}|"

        # Extract the branch from this entry.
        local rest="${entry#*|}"
        local branch="${rest%%|*}"

        local owner="${repo_key%%/*}"
        local repo="${repo_key#*/}"
        local clone_dir="$EXTERNAL_DIR/.repos/${owner}-${repo}"
        local paths
        paths="$(collect_paths_for_repo "$repo_key")"

        # Read the previously locked SHA before fetching.
        local old_sha
        old_sha="$(read_locked_sha "$repo_key")"

        clone_or_update_repo "$repo_key" "$branch" "$clone_dir" "$paths"

        # Get the new HEAD and show what changed.
        local new_sha
        new_sha="$(git -C "$clone_dir" rev-parse HEAD 2>/dev/null || echo "")"

        if [[ -z "$old_sha" && -n "$new_sha" ]]; then
            echo "  new       $repo_key (first fetch, locked at ${new_sha:0:12})"
        elif [[ -n "$old_sha" && -n "$new_sha" && "$old_sha" != "$new_sha" ]]; then
            if ! show_changelog "$clone_dir" "$repo_key" "$old_sha" "$new_sha" "$paths"; then
                echo "  current   $repo_key (upstream has new commits but skill files unchanged)"
            fi
        else
            echo "  current   $repo_key (no changes)"
        fi

        copy_skills_from_repo "$clone_dir" "$paths"

        # Update the lockfile with the new SHA.
        if [[ -n "$new_sha" ]]; then
            write_locked_sha "$repo_key" "$new_sha"
        fi
    done

    echo ""
}

# remove_stale_personal_symlinks
#   Removes global symlinks that point into SKILLS_SRC but whose target
#   either no longer exists (skill deleted) or has gained an OPTIN file
#   (skill moved from global to opt-in). Per-repo symlinks created by
#   --link-into are not touched here; they live outside TARGET_DIR.
remove_stale_personal_symlinks() {
    for link in "$TARGET_DIR"/*; do
        [[ -L "$link" ]] || continue
        local target
        target="$(readlink "$link")"
        case "$target" in
            "$SKILLS_SRC"/*)
                if [[ ! -d "$target" ]]; then
                    echo "  remove    $(basename "$link") (skill folder deleted)"
                    rm "$link"
                elif [[ -f "${target%/}/$OPTIN_FILENAME" ]]; then
                    echo "  remove    $(basename "$link") from global (now opt-in)"
                    rm "$link"
                fi
                ;;
        esac
    done
}

# ── Personal skills ──────────────────────────────────────────────────────

# install_personal_skills
#   Walks skills/ and symlinks each skill globally, except those marked
#   opt-in by an OPTIN file. Opt-in skills are installed per repo with
#   --link-into.
install_personal_skills() {
    echo "Personal skills:"
    remove_stale_personal_symlinks
    for skill_dir in "$SKILLS_SRC"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local skill_name
        skill_name="$(basename "$skill_dir")"
        if [[ -f "${skill_dir%/}/$OPTIN_FILENAME" ]]; then
            echo "  skip      $skill_name (opt-in — use --link-into)"
            continue
        fi
        symlink_skill "$skill_dir" "$skill_name"
    done
}

# ── --link-into mode ───────────────────────────────────────────────────

# link_into <project_path> <skill_name>
#   One-shot: symlink a single skill into <project_path>/.claude/skills/
#   and exit. Used for opt-in skills. The project path must already exist;
#   the .claude/skills/ subdirectory is created if needed.
link_into() {
    local project_path="$1"
    local skill_name="$2"

    if [[ ! -d "$project_path" ]]; then
        echo "Error: project path not found: $project_path" >&2
        exit 1
    fi

    local skill_dir="$SKILLS_SRC/$skill_name"
    if [[ ! -d "$skill_dir" ]]; then
        echo "Error: skill not found: $skill_name (looked in $SKILLS_SRC)" >&2
        exit 1
    fi

    # Resolve to an absolute, canonical path so the symlink target is
    # stable regardless of how the user invoked the script.
    project_path="$(cd "$project_path" && pwd)"
    local project_skills_dir="$project_path/.claude/skills"
    mkdir -p "$project_skills_dir"

    echo "Installing $skill_name into $project_path:"
    ensure_symlink "$skill_dir" "$project_skills_dir/$skill_name" "$skill_name"
    echo ""
    echo "Done. $linked linked, $up_to_date already up to date, $conflicts conflicts."
}

# ── External skills ──────────────────────────────────────────────────────

# install_external_skills
#   Fetches skills from the manifest, cleans up stale symlinks, and
#   symlinks the fetched skills into TARGET_DIR.
install_external_skills() {
    fetch_external_skills
    remove_stale_external_symlinks

    [[ -d "$EXTERNAL_DIR" ]] || return

    local has_external_skills=false
    for skill_dir in "$EXTERNAL_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local skill_name
        skill_name="$(basename "$skill_dir")"
        # Skip the .repos cache directory — it's not a skill.
        [[ "$skill_name" == ".repos" ]] && continue
        if [[ "$has_external_skills" == false ]]; then
            echo ""
            echo "External skills:"
            has_external_skills=true
        fi
        symlink_skill "$skill_dir" "$skill_name"
    done
}

# ── Main ─────────────────────────────────────────────────────────────────

if [[ -n "$LINK_INTO_PATH" ]]; then
    link_into "$LINK_INTO_PATH" "$LINK_INTO_SKILL"
    exit 0
fi

mkdir -p "$TARGET_DIR"
install_claude_md
echo ""
install_personal_skills
install_external_skills
echo ""
echo "Done. $linked linked, $up_to_date already up to date, $conflicts conflicts."
