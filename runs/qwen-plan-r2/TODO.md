# TODO

## Goal
Build a tiny CLI todo manager in Python 3.11+ using only stdlib, with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Project scaffolding
- [x] Create `tests/__init__.py`
- [x] Create `README.md` with brief usage examples

### 2. Core logic — `todo.py`
- [x] Implement argparse CLI with subcommands: `add`, `list`, `done`, `rm`, `clear`
- [x] Implement JSON persistence (load/save `todos.json`, create if missing)
- [x] Implement todo schema: integer `id`, string `title`, boolean `done`
- [x] Implement monotonically increasing IDs (never reused after `rm`)
- [x] Implement error handling: invalid/missing IDs print to stderr and exit non-zero (no stack traces)

### 3. Tests — `tests/test_todo.py`
- [x] Write test for `add` command (verify ID assignment)
- [x] Write test for `list` command (verify output format `[ID] [x|·] title`)
- [x] Write test for `done` command (verify done flag toggled)
- [x] Write test for `rm` command (verify deletion, ID not reused)
- [x] All tests use a temp directory for `todos.json`

### 4. Verification
- [x] Run `pytest tests/` and confirm all tests pass
- [x] Manually verify CLI commands work end-to-end

## Notes
- Python 3.11+, stdlib only (`json`, `argparse`, `sys`, `os`, `tempfile`, `pytest` for tests).
- Single file `todo.py` chosen for layout (reasonable for this scope).
- `todos.json` stored in current working directory.
- Error messages go to stderr; exit code is non-zero on errors.
