---
name: python-dev-process
description: Christian's Python development process: phases, tooling, testing, refactoring discipline. Use when starting Python projects, structuring or refactoring code, adding tests or linting. Triggers include "set up a new project", "add tests", "refactor this".
---

# Python Development Process

Apply whether starting a new project or contributing to an existing one.

---

## Development phases

A vocabulary for what kind of work you're doing right now, not a one-way progression. New features cycle back through phases 1–3 at a smaller scale.

### Phase 1: Get it working

A working implementation, no guardrails yet. For a new project:

- Working core functionality.
- A PRD or README explaining what the project does and why.
- A `.gitignore` with standard Python entries (`.venv`, `__pycache__`, `.pyc`, `.pytest_cache`, `.ruff_cache`, `.env`, `.DS_Store`).
- A `pyproject.toml` with dependencies via `uv add`.
- A clear first commit.

Skip linting, formatting, hooks, tests, and module extraction for now. For a new feature in a project that already has guardrails, go straight to Phase 2.

### Phase 2: Add guardrails

Set up the toolchain. For a new project, in this order:

1. **Unit tests** for core logic. Test your code, not third-party libraries. Mock external services. Use `monkeypatch` and `tmp_path` for file I/O.
2. **Ruff** for lint and format: `uv add --group dev ruff`.
3. **Pre-commit hook** via `prek` that rejects commits failing lint or format checks.
4. **AGENTS.md** (and a minimal CLAUDE.md pointing to it). Use `assets/AGENTS-template.md` as the starting point, customized.

### Phase 3: Extract and modularize

Refactor when the code gets tangled, whether early or months later. Each extraction is a single focused commit:

- **Presentation separate from logic.** UI code (Streamlit, Flask, CLI) contains no business logic. Business logic has no UI imports.
- **One responsibility per module.** Split when a module does two distinct things. Name modules after what they do, not what framework they use.
- **Constants for magic values.** Define key names, prompt names, and config values as constants in the owning module.
- **Accessor functions over raw dict access.** Expose accessors instead of letting callers dig into internal dicts.
- **Move tests alongside the code.** Tests in `tests/` mirror the module structure. Move or create tests in the same commit as the extraction.

Each extraction commit: move or extract the code, update or add tests, update AGENTS.md.

### Phase 4: Evolve with confidence

- Run tests after every change to a logic module.
- Remove dead code when you find it.
- Update AGENTS.md in the same commit when architecture changes.
- One concern per commit. Refactor, feature, and bug-fix commits stay separate.

---

## Tooling

- **Ruff** (lint + format, replaces flake8/black/isort): `uv run ruff check .` and `uv run ruff format .`. Configure in `pyproject.toml` if defaults aren't enough.
- **pytest**: tests in `tests/`. Configure in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  pythonpath = ["."]
  ```
- **prek** for pre-commit hooks (Rust-native, faster than the Python `pre-commit` tool). See the `modern-python` skill for setup.
- **Dev servers**: kill any existing process on the target port first. Example: `lsof -ti:8501 | xargs kill` before `uv run streamlit run app.py`.
- **uv** manages the venv. Use `uv run <cmd>` instead of activating manually.
- **Dependencies** live in `pyproject.toml`, managed via `uv add` / `uv remove`. Use `[dependency-groups]` (PEP 735), not `[project.optional-dependencies]`. Commit `uv.lock`.

```bash
uv add requests rich            # runtime
uv add --group dev pytest ruff  # dev
uv sync --all-groups            # install everything
```

---

## Testing philosophy

- Test your logic, trust third-party libraries. Don't retest JSON parsing or RIS reading.
- Mock external services (LLM calls, API requests, DB connections). Never make real network calls in tests.
- Use `monkeypatch` and `tmp_path` for filesystem tests. Never write to real project files.
- Don't test the UI layer with framework-specific harnesses. The UI should have no business logic, so there's little to test.
- Test names describe behavior: `test_batch_screen_continues_on_per_paper_error`, not `test_batch_screen_3`.
- Test edge cases and error paths: empty inputs, malformed data, missing fields, network failures. The happy path is necessary but not sufficient.

---

## Code style

- Python 3.12+ features (`list[dict]` not `typing.List[Dict]`).
- Docstrings on public functions in logic modules. Not on test functions or obvious helpers.
- Type hints on logic-module function signatures. Not on test functions.
- `NamedTuple` or `dataclass` for structured data crossing module boundaries.

---

## AGENTS.md and CLAUDE.md

Every project gets both.

**CLAUDE.md** is one line:
```
See [AGENTS.md](AGENTS.md) for project guidelines.
```

**AGENTS.md** is the real document. See `assets/AGENTS-template.md` for the template. Key sections:

- **Project overview**: what the project does, link to full spec.
- **Architecture**: every module, one line each, describing its responsibility and what it must not import. Most important section. Encodes the module boundaries.
- **Setup**: install deps and set up hooks.
- **Running tests**: exact command, plus which modules require test runs after changes.
- **Linting and formatting**: Ruff commands, how the pre-commit hook works.
- **Code style**: project-specific conventions.
- **Testing philosophy**: what to mock, what to trust, what not to test.

Update AGENTS.md in the same commit as architecture changes.

---

## Refactoring signals

Refactor when:

- A module does two things that could change independently.
- Multiple modules import from the same module to access different concerns.
- A function is longer than ~50 lines.
- The same pattern appears in multiple places.
- Dead code exists.
- AGENTS.md doesn't match the actual code.

Each refactoring is its own commit. Never combined with a feature or bug fix.

---

## Starting a new project

1. `uv init` (or `uv init --package` for distributable packages). Initialize Git.
2. `uv add` runtime deps. `uv add --group dev pytest ruff` for dev tools.
3. Standard `.gitignore`.
4. Build the first working version (Phase 1). Commit.
5. Add tests, prek hooks, AGENTS.md, CLAUDE.md (Phase 2). Use `assets/AGENTS-template.md` customized.
6. Commit each guardrail addition separately.
7. Continue with Phase 3 and 4 as the project grows.
