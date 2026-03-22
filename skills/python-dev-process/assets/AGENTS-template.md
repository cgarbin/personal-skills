# Agent Guidelines

## Project overview

<!-- One or two sentences: what does this project do? -->
<!-- Link to PRD or detailed spec if one exists. -->

## Architecture

<!-- One line per module. State its responsibility and what it must NOT import. This section encodes module boundaries — keep it current. -->

- `app.py` — UI only. No business logic.

<!-- Example entries (delete these and replace with actual modules):
- `screening.py` — Screening logic. Calls `llm_provider.call_llm()`. No direct API client imports.
- `results.py` — Result persistence and accessors. No UI imports.
- `parser.py` — File parsing. No UI or API imports.
-->

## Setup

```bash
uv sync --all-groups
```

This installs all runtime and dev dependencies. `uv` manages the virtual environment automatically. Use `uv run <cmd>` to execute commands.

## Running tests

Tests live in the `tests/` directory. Configuration is in `pyproject.toml`.

```bash
uv run pytest tests/ -v
```

Run tests after every change to logic modules.
<!-- List the modules that require test runs after changes, e.g.:
Run tests after every change to `parser.py`, `screening.py`, `results.py`.
-->

## Linting and formatting

Ruff handles both linting and formatting. Pre-commit hooks via `prek` reject commits that fail either check.

```bash
uv run ruff check .        # lint
uv run ruff format .       # format
```

## Code style

- Python 3.12+ features are fine (type hints with `list[dict]`, etc.).
- No type stubs or docstrings required on test functions.
- Use `monkeypatch` and `tmp_path` for file I/O tests — never write to real project files.
- Mock external services in tests — never make real API calls.

## Testing philosophy

- Trust third-party libraries to parse their own formats. Test our logic on top of their output: field extraction, fallbacks, filtering.
- Don't test the UI layer with framework-specific test harnesses — the business logic is already covered through the logic module tests.
