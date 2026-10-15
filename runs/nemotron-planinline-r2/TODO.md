# TODO

## Goal
Build a small command-line todo app at the working directory using Python 3.11+ stdlib only (except pytest for tests), following the functional requirements and layout from SPEC.md.

## Tasks

### 1. Project Setup
- [x] Create `todo.py` with argparse subcommands (add, list, done, rm, clear)
- [x] Set up `todos.json` persistence at `./todos.json`
- [x] Implement monotonically increasing IDs that are never reused

### 2. Core Functionality
- [x] Implement `add <title>` command — add new todo, print new ID
- [x] Implement `list` command — print all todos as `[ID] [x|·] title`. `x` = done, `·` = open.
- [x] Implement `done <id>` command — mark a todo done by ID
- [x] Implement `rm <id>` command — delete a todo by ID
- [x] Implement `clear` command — remove all done todos

### 3. Error Handling
- [x] Missing/invalid IDs should print clear error to stderr and exit non-zero
- [x] Don't crash with a stack trace on errors

### 4. Tests
- [x] Create `tests/test_todo.py` with at least 4 pytest tests covering add, list, done, rm
- [x] Use a temp directory for the JSON file during tests (don't pollute cwd)
- [x] Ensure tests pass with `pytest tests/`

### 5. Documentation
- [x] Create `README.md` with brief description and usage examples

## Notes
- Language: Python 3.11+, stdlib only (except pytest for tests)
- No external runtime deps
- IDs must be monotonically increasing — never reused even after rm
- Tests should pass with pytest
- Code should be readable — type hints encouraged but not required