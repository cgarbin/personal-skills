---
name: python-dev-process
description: "Christian's Python development process and practices. Use this skill whenever Christian starts a new Python project, asks you to set up a project, asks for help structuring or refactoring Python code, or when working on any Python codebase. Also trigger when he says 'set up a new project', 'add tests', 'add linting', 'refactor this', or asks about project structure, testing strategy, or code organization for Python. If Christian is writing Python code with you, consult this skill to follow his development practices."
---

# Python Development Process

This skill captures how Christian develops Python projects, derived from his
actual practices (especially the title-abstract-screening project built
entirely with Claude Code). It covers the development lifecycle, tooling
choices, code organization, testing philosophy, and refactoring discipline.

When working on a Python project with Christian, follow these practices.
They apply whether you're starting a new project or contributing to an
existing one.

---

## Development phases

Projects evolve through phases. Each phase has a clear purpose. Don't skip
ahead — get the current phase right before moving to the next one.

### Phase 1: Get it working

Start with a functional version. The first priority is something that runs
and does what it's supposed to do. Don't worry about code quality tooling,
perfect modularity, or comprehensive tests yet.

What belongs in this phase:

- A working implementation of the core functionality.
- A PRD or README that explains what the project does and why.
- A `.gitignore` with standard Python entries (venv, `__pycache__`, `.pyc`,
  `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.env`, `.DS_Store`).
- A `requirements.txt` with pinned minimum versions of dependencies.
- A clear first commit.

What doesn't belong yet: linting, formatting, pre-commit hooks, tests,
module extraction. Those come next.

### Phase 2: Add guardrails

Once the code works, add the infrastructure that keeps it working.

In this order:

1. **Unit tests** for the core logic modules. Test your code, not
   third-party libraries. Mock external services (APIs, databases) — never
   make real calls in tests. Use `monkeypatch` and `tmp_path` for file I/O.
2. **Ruff** for linting and formatting. Add it to `requirements-dev.txt`.
3. **Pre-commit hook** that rejects commits failing lint or format checks.
   Keep the hook in `scripts/pre-commit` and symlink it during setup.
4. **AGENTS.md** (and a minimal CLAUDE.md pointing to it) to tell Claude
   how the project is structured and how to work in it.

See the `assets/AGENTS-template.md` bundled with this skill for a starting
point for AGENTS.md. Customize it for each project.

### Phase 3: Extract and modularize

As the codebase grows, extract modules. Each extraction should be a single,
focused commit. The pattern:

- **Presentation separate from logic.** UI code (Streamlit, Flask, CLI)
  should contain no business logic. Business logic should have no UI imports.
- **One responsibility per module.** When a module does two distinct things,
  split it. Name the modules after what they do, not what framework they use.
- **Constants for magic values.** Define key names, prompt names, and
  configuration values as constants in the module that owns them.
- **Accessor functions over raw dict access.** When other modules need data
  from a module's internal structures, expose accessor functions rather than
  letting callers dig into dicts directly.
- **Move tests alongside the code.** Tests live in `tests/` and mirror the
  module structure. When you extract a module, move or create its tests in
  the same commit.

Each extraction commit should:

1. Move or extract the code.
2. Update or add tests.
3. Update AGENTS.md to reflect the new module.

### Phase 4: Evolve with confidence

With tests, linting, and clean modules in place, new features land cleanly.
This phase is ongoing. The practices:

- **Run tests after every change** to a logic module.
- **Remove dead code** when you find it — don't leave it commented out.
- **Update docs when code changes.** If AGENTS.md describes the architecture
  and the architecture changes, update AGENTS.md in the same commit.
- **One concern per commit.** A refactoring commit should not also add a
  feature. A bug fix should not also restructure a module. This makes the
  history useful for understanding what changed and why.

---

## Tooling

### Ruff (linting and formatting)

Ruff handles both linting and formatting. No need for separate tools
(flake8, black, isort). Configure it in `pyproject.toml` if needed,
but the defaults are usually fine.

```bash
ruff check .        # lint
ruff format .       # format
```

### pytest

Tests live in `tests/`. Configure in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

### Pre-commit hook

The hook lives in `scripts/pre-commit` (tracked in Git) and gets symlinked
into `.git/hooks/` during setup. It runs Ruff lint and format checks on
staged Python files only, and rejects the commit if either fails.

### Virtual environment

Use `uv` when available (faster), fall back to standard `venv`:

```bash
uv venv --python 3.14 venv    # or: python -m venv venv
source venv/bin/activate
uv pip install -r requirements-dev.txt
```

### Dependency files

- `requirements.txt` — runtime dependencies with minimum versions
  (e.g., `streamlit>=1.54.0`).
- `requirements-dev.txt` — includes runtime deps plus dev tools:
  ```
  -r requirements.txt
  pytest>=8.0.0
  ruff>=0.11.0
  ```

---

## Testing philosophy

- **Test your logic, trust third-party libraries.** If a library parses
  JSON or reads RIS files, don't retest that. Test the logic you build on
  top of its output: field extraction, fallbacks, filtering, error handling.
- **Mock external services.** Mock LLM calls, API requests, and database
  connections. Never make real network calls in tests.
- **Use `monkeypatch` and `tmp_path`** for tests that touch the filesystem.
  Never write to real project files from tests.
- **Don't test the UI layer** with framework-specific test harnesses (e.g.,
  Streamlit's test runner). The business logic is already covered through
  the logic module tests. If the UI layer has no business logic (as it
  shouldn't), there's little to test.
- **Test names describe behavior.** `test_batch_screen_continues_on_per_paper_error`
  not `test_batch_screen_3`.
- **Test edge cases and error paths.** Empty inputs, malformed data, missing
  fields, network failures. The happy path is necessary but not sufficient.

---

## Code style

- Python 3.11+ features are fine (e.g., `list[dict]` type hints instead
  of `typing.List[Dict]`).
- Docstrings on public functions in logic modules. Not required on test
  functions or obvious helpers.
- Type hints on function signatures for logic modules. Not required on
  test functions.
- Use `NamedTuple` or `dataclass` for structured data over raw dicts when
  a structure is used across module boundaries.

---

## AGENTS.md and CLAUDE.md

Every project gets both files. They serve different purposes:

**CLAUDE.md** is minimal — typically one line pointing to AGENTS.md:
```
See [AGENTS.md](AGENTS.md) for project guidelines.
```

**AGENTS.md** is the real document. It tells Claude (and other developers)
how to work in this specific project. See `assets/AGENTS-template.md` for
the template. The key sections:

- **Project overview** — what the project does, where to find the full spec.
- **Architecture** — every module, one line each, describing its
  responsibility and what it must not import. This is the most important
  section. It encodes the module boundaries.
- **Setup** — how to create the venv, install deps, set up the hook.
- **Running tests** — the exact command, plus which modules require test
  runs after changes.
- **Linting and formatting** — Ruff commands, how the pre-commit hook works.
- **Code style** — project-specific conventions.
- **Testing philosophy** — what to mock, what to trust, what not to test.

Update AGENTS.md every time the architecture changes. If you extract a new
module, add it to the architecture section in the same commit.

---

## Refactoring discipline

Refactoring is a first-class activity, not something that happens "when
we have time." These are the signals that a refactoring is needed:

- A module does two things that could change independently.
- Multiple modules import from the same module to access different
  concerns (e.g., both UI and logic imports from one file).
- A function is longer than roughly 50 lines.
- The same pattern appears in multiple places (extract it).
- Dead code exists (remove it).
- AGENTS.md doesn't match the actual code (either update the doc or fix
  the code).

Each refactoring is its own commit with a descriptive message. Never
combine a refactoring with a feature addition or bug fix.

---

## Starting a new project

When Christian asks to start a new Python project:

1. Create the project directory and initialize Git.
2. Create `requirements.txt`, `requirements-dev.txt`, `.gitignore`,
   and a virtual environment.
3. Build the first working version (Phase 1).
4. Commit the working version.
5. Add tests, Ruff, pre-commit hook, AGENTS.md, CLAUDE.md (Phase 2).
   Use `assets/AGENTS-template.md` as the starting point for AGENTS.md,
   customized for this project.
6. Commit each guardrail addition separately.
7. Continue with Phase 3 and 4 as the project grows.
