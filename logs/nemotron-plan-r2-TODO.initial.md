# Plan: Tiny CLI Todo Manager

## Overview
Build a small command-line todo app using Python 3.11+ stdlib only (except pytest for tests).

## Features
- `add <title>` — add new todo, prints new ID
- `list` — print all todos as `[ID] [x|·] title`
- `done <id>` — mark todo done by ID
- `rm <id>` — delete todo by ID
- `clear` — remove all done todos

## Constraints
- Python 3.11+ stdlib only
- JSON persistence at `./todos.json`
- Monotonically increasing IDs (never reused)
- argparse with subcommands
- Error handling: missing/invalid IDs → stderr + non-zero exit, no stack traces
- Tests in `tests/test_todo.py` using temp directory
- README.md with usage examples

## Files to create/modify
1. `todo.py` — main CLI application
2. `tests/test_todo.py` — pytest tests (at least 4 tests covering add, list, done, rm)
3. `README.md` — brief usage examples

## Execution order
1. Create `todo.py` with all CLI functionality
2. Create `tests/test_todo.py` with pytest tests
3. Create `README.md`
4. Run `pytest tests/` to verify