#!/usr/bin/env bash
# Install personal and external skills by symlinking them into the Claude
# skills directory, and symlink the global CLAUDE.md into ~/.claude/.
#
# Usage:
#   ./scripts/install.sh                                 # repo = parent of this script's dir
#   ./scripts/install.sh /path/to/repo                   # explicit repo path
#   ./scripts/install.sh --target ~/.claude/skills       # custom target dir
#   ./scripts/install.sh --link-into <skills-dir> <skill>  # opt-in per repo
#
# A folder is a skill only if it holds a SKILL.md. Folders without one are
# never installed, and an existing symlink to one is removed.
#
# Personal skills default to global (symlinked into TARGET_DIR). A skill
# becomes opt-in by placing an empty OPTIN file next to its SKILL.md.
# Opt-in skills are skipped by the normal install pass and must be
# installed per repo with --link-into.
#
# The script:
#   1. Symlinks the global CLAUDE.md from <repo>/claude-md/
#   2. Cleans up stale personal skill symlinks (deleted, no SKILL.md, or
#      now opt-in)
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
                echo "Error: --link-into requires <skills-dir> <skill-name>." >&2
                exit 1
            fi
            LINK_INTO_PATH="$2"
            LINK_INTO_SKILL="$3"
            shift 3
            ;;
        -h|--help)
            echo "Usage: $0 [REPO_DIR] [--target SKILLS_DIR]"
            echo "       $0 --link-into <skills-dir> <skill-name>"
            echo ""
            echo "  REPO_DIR       Path to the personal-skills repository."
            echo "                 Defaults to the parent of the directory holding"
            echo "                 this script."
            echo "  --target       Claude skills directory to symlink into."
            echo "                 Default: ~/.claude/skills"
            echo "  --link-into    One-shot: symlink <skill-name> into"
            echo "                 <skills-dir> and exit. <skills-dir> must end in"
            echo "                 .claude/skills (same shape as --target). Use"
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

# Canonicalize even when the caller passed the path. A relative path would
# be stored verbatim in every symlink and resolve against the link's own
# directory, and a trailing slash (what tab-completion produces) doubles the
# separator in SKILLS_SRC, which stops the stale-symlink patterns matching.
if [[ ! -d "$REPO_DIR" ]]; then
    echo "Error: repo directory not found: $REPO_DIR" >&2
    exit 1
fi
REPO_DIR="$(cd "$REPO_DIR" && pwd)"

SKILLS_SRC="$REPO_DIR/skills"
EXTERNAL_DIR="$REPO_DIR/from-others"
MANIFEST="$REPO_DIR/skills.manifest"
LOCKFILE="$REPO_DIR/skills.lock"
CLAUDE_MD_SRC="$REPO_DIR/claude-md/CLAUDE.md"
CLAUDE_MD_TARGET="$HOME/.claude/CLAUDE.md"
OPTIN_FILENAME="OPTIN"
SKILL_FILENAME="SKILL.md"

if [[ ! -d "$SKILLS_SRC" ]]; then
    echo "Error: skills directory not found at $SKILLS_SRC" >&2
    exit 1
fi

# Reject a --target or --link-into that points at the wrong place. The
# path must end in .claude/skills so a typo cannot scatter symlinks into
# an unrelated directory. Trailing slash is tolerated.
require_skills_dir() {
    local flag="$1"
    local path="$2"
    # Reject relative paths up front. Otherwise a missing leading slash lets
    # the path be resolved against the cwd, silently creating a doubled tree.
    if [[ "$path" != /* ]]; then
        echo "Error: $flag must be an absolute path (got: $path)" >&2
        exit 1
    fi
    if [[ "${path%/}" != *"/.claude/skills" ]]; then
        echo "Error: $flag must end in .claude/skills (got: $path)" >&2
        exit 1
    fi
}

require_skills_dir "--target" "$TARGET_DIR"
if [[ -n "$LINK_INTO_PATH" ]]; then
    require_skills_dir "--link-into" "$LINK_INTO_PATH"
fi

# ── Counters ─────────────────────────────────────────────────────────────

linked=0
up_to_date=0
conflicts=0
removed=0

# Names a cleanup pass already reported this run, newline separated.
# Without it the same folder prints a remove line and a skip line, which
# reads like two different things happened.
handled=""

# The External header is printed on first use so an empty from-others adds
# no section. Both the cleanup pass and the install loop can be first.
external_header_printed=false

# ── Skill detection ──────────────────────────────────────────────────────

# is_skill <dir>
#   True when the folder holds a SKILL.md, which is what makes it a skill
#   rather than a workspace or a stray folder.
#
#   The name is compared against the directory entry instead of tested with
#   -f, which is case-insensitive on macOS. Otherwise a folder holding
#   skill.md installs here and is skipped on Linux from the same checkout.
is_skill() {
    local entry
    for entry in "${1%/}"/*; do
        [[ "${entry##*/}" == "$SKILL_FILENAME" && -f "$entry" ]] && return 0
    done
    return 1
}

# was_handled <name>
#   True when a cleanup pass already reported this folder.
was_handled() {
    [[ $'\n'"$handled" == *$'\n'"$1"$'\n'* ]]
}

# mark_handled <name>
mark_handled() {
    handled+="$1"$'\n'
}

# print_external_header
#   Emits the External section header once, whichever pass reaches it first.
print_external_header() {
    if [[ "$external_header_printed" == false ]]; then
        echo ""
        echo "External skills:"
        external_header_printed=true
    fi
}

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
        return 0
    fi

    # Stale symlink (points elsewhere or is broken). Safe to replace.
    if [[ -L "$link_path" ]]; then
        echo "  update    $display_name (re-linking)"
        rm "$link_path"
    # Non-symlink file or folder. Don't touch it.
    elif [[ -e "$link_path" ]]; then
        echo "  CONFLICT  $display_name (a file or folder already exists at $link_path)" >&2
        echo "            Remove or rename it, then re-run this script." >&2
        conflicts=$((conflicts + 1))
        return 0
    fi

    ln -s "$src" "$link_path"
    echo "  link      $display_name -> $src"
    linked=$((linked + 1))
}

# symlink_skill <source_dir> <skill_name>
#   Symlinks a skill into TARGET_DIR.
symlink_skill() {
    ensure_symlink "$1" "$TARGET_DIR/$2" "$2"
}

# remove_stale_external_symlinks
#   Removes symlinks in TARGET_DIR that point into EXTERNAL_DIR but whose
#   target no longer exists (i.e. the skill was removed from the manifest).
remove_stale_external_symlinks() {
    for link in "$TARGET_DIR"/*; do
        # Only inspect symlinks. Skip regular files and folders.
        [[ -L "$link" ]] || continue
        local target
        target="$(readlink "$link")"
        case "$target" in
            "$EXTERNAL_DIR"/*)
                if [[ ! -d "$target" ]]; then
                    print_external_header
                    echo "  remove    $(basename "$link") (no longer in manifest)"
                    rm "$link"
                    removed=$((removed + 1))
                    mark_handled "$(basename "$link")"
                elif ! is_skill "$target"; then
                    print_external_header
                    echo "  remove    $(basename "$link") (no $SKILL_FILENAME)"
                    rm "$link"
                    removed=$((removed + 1))
                    mark_handled "$(basename "$link")"
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
#   Uses awk + temp file (rather than sed -i) so the script stays portable
#   across BSD and GNU userlands.
write_locked_sha() {
    local repo_key="$1"
    local sha="$2"

    # Rewriting churns a tracked file's mtime for nothing when the SHA matches.
    if [[ "$(read_locked_sha "$repo_key")" == "$sha" ]]; then
        return 0
    fi

    local tmp="${LOCKFILE}.tmp"
    local input="$LOCKFILE"
    [[ -f "$input" ]] || input=/dev/null

    awk -v key="$repo_key" -v sha="$sha" '
        $1 == key { print key, sha; found=1; next }
        { print }
        END { if (!found) print key, sha }
    ' "$input" > "$tmp"
    sort -o "$tmp" "$tmp"
    mv "$tmp" "$LOCKFILE"
}

# prune_lockfile
#   Drops lock entries for repos the manifest no longer lists. write_locked_sha
#   only upserts, so nothing else ever removes them.
prune_lockfile() {
    [[ -f "$LOCKFILE" ]] || return 0

    # bash 3.2 has no associative arrays, so membership is a substring test.
    local keys=""
    if [[ ${#manifest_entries[@]} -gt 0 ]]; then
        for entry in "${manifest_entries[@]}"; do
            keys="${keys}|${entry%%|*}|"
        done
    fi

    local tmp="${LOCKFILE}.tmp"
    local dropped=0
    local repo_key
    local sha
    : > "$tmp"
    # A loop, not awk: kept lines go to the temp file, messages to stdout.
    while read -r repo_key sha || [[ -n "$repo_key" ]]; do
        [[ -z "$repo_key" ]] && continue
        if [[ "$keys" == *"|${repo_key}|"* ]]; then
            echo "$repo_key $sha" >> "$tmp"
        else
            echo "  unlock    $repo_key (no longer in manifest)"
            dropped=1
        fi
    done < "$LOCKFILE"

    if [[ $dropped -eq 1 ]]; then
        sort -o "$tmp" "$tmp"
        mv "$tmp" "$LOCKFILE"
    else
        rm -f "$tmp"
    fi
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
#   Symlinks <repo>/claude-md/CLAUDE.md → CLAUDE_MD_TARGET, but only when
#   nothing is there yet. Unlike a skill folder, the global CLAUDE.md is a
#   file the machine may already own, so install never replaces what it
#   finds, not even a symlink it did not create.
#   Skips if claude-md/CLAUDE.md doesn't exist in the repo.
install_claude_md() {
    [[ -f "$CLAUDE_MD_SRC" ]] || return 0

    mkdir -p "$(dirname "$CLAUDE_MD_TARGET")"
    echo "CLAUDE.md:"

    if [[ -L "$CLAUDE_MD_TARGET" && "$(readlink "$CLAUDE_MD_TARGET")" == "$CLAUDE_MD_SRC" ]]; then
        echo "  ok        CLAUDE.md (already linked)"
        up_to_date=$((up_to_date + 1))
        return 0
    fi

    # -e follows the link, so a dangling symlink reads as absent. -L catches it.
    if [[ -e "$CLAUDE_MD_TARGET" || -L "$CLAUDE_MD_TARGET" ]]; then
        echo "  skip      CLAUDE.md ($CLAUDE_MD_TARGET already exists)"
        echo "            Remove it and re-run if you want to use this repo's copy."
        return 0
    fi

    ln -s "$CLAUDE_MD_SRC" "$CLAUDE_MD_TARGET"
    echo "  link      CLAUDE.md -> $CLAUDE_MD_SRC"
    linked=$((linked + 1))
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
    # bash 3.2 trips set -u on an empty array.
    if [[ ${#manifest_entries[@]} -eq 0 ]]; then
        return 0
    fi
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
            echo "  ERROR     $skill_name (path $skill_path not found)" >&2
        fi
    done <<< "$paths"
}

# fetch_external_skills
#   Reads the manifest, prunes stale lock entries, clones/updates repos, and
#   copies skill folders.
fetch_external_skills() {
    [[ -f "$MANIFEST" ]] || return 0

    manifest_entries=()
    parse_manifest
    # An empty manifest orphans every entry, so prune before the early return.
    prune_lockfile

    mkdir -p "$EXTERNAL_DIR"
    # Emptying the manifest must still remove what earlier runs fetched.
    clean_external_skills

    # No entries means no external skills. The caller clears stale symlinks.
    if [[ ${#manifest_entries[@]} -eq 0 ]]; then
        return 0
    fi

    echo "Fetching external skills..."
    echo ""

    # Deduplicate repos so we clone each once. Uses string matching because
    # bash 3.2 lacks associative arrays.
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
#   no longer exists (skill deleted), lost its SKILL.md, or gained an
#   OPTIN file (skill moved from global to opt-in). Per-repo symlinks
#   created by --link-into are not touched here. They live outside
#   TARGET_DIR.
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
                    removed=$((removed + 1))
                    mark_handled "$(basename "$link")"
                elif ! is_skill "$target"; then
                    echo "  remove    $(basename "$link") (no $SKILL_FILENAME)"
                    rm "$link"
                    removed=$((removed + 1))
                    mark_handled "$(basename "$link")"
                elif [[ -f "${target%/}/$OPTIN_FILENAME" ]]; then
                    echo "  remove    $(basename "$link") from global (now opt-in)"
                    rm "$link"
                    removed=$((removed + 1))
                    mark_handled "$(basename "$link")"
                fi
                ;;
        esac
    done
}

# ── Personal skills ──────────────────────────────────────────────────────

# install_personal_skills
#   Walks skills/ and symlinks each skill globally, skipping folders with
#   no SKILL.md and those marked opt-in by an OPTIN file. Opt-in skills
#   are installed per repo with --link-into.
install_personal_skills() {
    echo "Personal skills:"
    remove_stale_personal_symlinks
    for skill_dir in "$SKILLS_SRC"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local skill_name
        skill_name="$(basename "$skill_dir")"
        # skill-creator writes eval workspaces next to the skill they test,
        # so skills/ holds folders that are not installable.
        if ! is_skill "$skill_dir"; then
            was_handled "$skill_name" ||
                echo "  skip      $skill_name (no $SKILL_FILENAME)"
            continue
        fi
        if [[ -f "${skill_dir%/}/$OPTIN_FILENAME" ]]; then
            echo "  skip      $skill_name (opt-in, use --link-into)"
            continue
        fi
        symlink_skill "$skill_dir" "$skill_name"
    done
}

# ── --link-into mode ───────────────────────────────────────────────────

# link_into <skills_dir> <skill_name>
#   One-shot: symlink a single skill into <skills_dir> and exit. Used for
#   opt-in skills. <skills_dir> must end in .claude/skills (validated
#   above) and is created if missing.
link_into() {
    local skills_dir="$1"
    local skill_name="$2"

    local skill_dir="$SKILLS_SRC/$skill_name"
    if [[ ! -d "$skill_dir" ]]; then
        echo "Error: skill not found: $skill_name (looked in $SKILLS_SRC)" >&2
        exit 1
    fi
    # Reject a name with a path separator. Otherwise ../elsewhere resolves to
    # a real skill outside skills/ and puts the symlink outside the
    # directory require_skills_dir just validated.
    if [[ "$skill_name" == */* ]]; then
        echo "Error: skill name must not contain '/' (got: $skill_name)" >&2
        exit 1
    fi
    if ! is_skill "$skill_dir"; then
        echo "Error: not a skill: $skill_name (no $SKILL_FILENAME in $skill_dir)" >&2
        exit 1
    fi

    mkdir -p "$skills_dir"
    # Resolve to a full absolute path so the symlink target is stable
    # regardless of how the user invoked the script.
    skills_dir="$(cd "$skills_dir" && pwd)"

    echo "Installing $skill_name into $skills_dir:"
    ensure_symlink "$skill_dir" "$skills_dir/$skill_name" "$skill_name"
    echo ""
    echo "Done. $linked linked, $up_to_date already up to date, $removed removed, $conflicts conflicts."
}

# ── External skills ──────────────────────────────────────────────────────

# install_external_skills
#   Fetches skills from the manifest, cleans up stale symlinks, and
#   symlinks the fetched skills into TARGET_DIR.
install_external_skills() {
    fetch_external_skills
    remove_stale_external_symlinks

    [[ -d "$EXTERNAL_DIR" ]] || return 0

    for skill_dir in "$EXTERNAL_DIR"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local skill_name
        skill_name="$(basename "$skill_dir")"
        # Skip the .repos cache directory. It's not a skill.
        [[ "$skill_name" == ".repos" ]] && continue
        print_external_header
        # A manifest path can point at a folder that is not a skill, for
        # instance when the upstream repo reorganizes and the path now
        # resolves to a parent directory.
        if ! is_skill "$skill_dir"; then
            was_handled "$skill_name" ||
                echo "  skip      $skill_name (no $SKILL_FILENAME)"
            continue
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
echo "Done. $linked linked, $up_to_date already up to date, $removed removed, $conflicts conflicts."
