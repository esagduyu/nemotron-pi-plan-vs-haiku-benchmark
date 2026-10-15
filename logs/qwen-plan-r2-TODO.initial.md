# TODO

## Goal
Build a tiny CLI todo manager in Python 3.11+ using only stdlib, with argparse subcommands, JSON persistence, and pytest tests.

## Tasks

### 1. Project scaffolding
- [ ] Create `tests/__init__.py`
- [ ] Create `README.md` with brief usage examples

### 2. Core logic — `todo.py`
- [ ] Implement argparse CLI with subcommands: `add`, `list`, `done`, `rm`, `clear`
- [ ] Implement JSON persistence (load/save `todos.json`, create if missing)
- [ ] Implement todo schema: integer `id`, string `title`, boolean `done`
- [ ] Implement monotonically increasing IDs (never reused after `rm`)
- [ ] Implement error handling: invalid/missing IDs print to stderr and exit non-zero (no stack traces)

### 3. Tests — `tests/test_todo.py`
- [ ] Write test for `add` command (verify ID assignment)
- [ ] Write test for `list` command (verify output format `[ID] [x|·] title`)
- [ ] Write test for `done` command (verify done flag toggled)
- [ ] Write test for `rm` command (verify deletion, ID not reused)
- [ ] All tests use a temp directory for `todos.json`

### 4. Verification
- [ ] Run `pytest tests/` and confirm all tests pass
- [ ] Manually verify CLI commands work end-to-end

## Notes
- Python 3.11+, stdlib only (`json`, `argparse`, `sys`, `os`, `tempfile`, `pytest` for tests).
- Single file `todo.py` chosen for layout (reasonable for this scope).
- `todos.json` stored in current working directory.
- Error messages go to stderr; exit code is non-zero on errors.
