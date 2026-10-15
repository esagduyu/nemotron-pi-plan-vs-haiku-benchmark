# TODO

## Goal
Build a stdlib-only Python CLI todo manager (`python todo.py <command>`) with JSON persistence, never-reused IDs, clean error handling, pytest tests, and a README.

## Tasks

### 1. Storage layer (`todo.py`)
- [x] Define the on-disk format: `{"next_id": int, "todos": [{"id": int, "title": str, "done": bool}, ...]}`
- [x] Implement `load(path) -> dict` that returns an empty store (`next_id: 1`, `todos: []`) when the file is missing
- [x] Make `load` raise a clear `TodoError` when the file contains invalid JSON or the wrong structure
- [x] Implement `save(path, data)` that writes atomically (temp file + `os.replace`)
- [x] Make the store path default to `./todos.json`, overridable via `TODO_FILE` env var (used by tests)

### 2. Core operations (`todo.py`)
- [x] `add_todo(data, title) -> int`: assigns `next_id`, increments it, returns the new ID; rejects empty/whitespace titles
- [x] `mark_done(data, id)`: raises `TodoError` if ID not found
- [x] `remove_todo(data, id)`: raises `TodoError` if ID not found; does not decrement `next_id`
- [x] `clear_done(data) -> int`: removes done todos, returns count removed
- [x] `format_todo(todo) -> str`: returns `[ID] [x|·] title`

### 3. CLI (`todo.py`)
- [x] Build an `argparse` parser with subcommands `add <title>`, `list`, `done <id>`, `rm <id>`, `clear`; `id` parsed with `type=int`
- [x] `add` prints the new ID; `list` prints one formatted line per todo (prints nothing when empty); `clear` prints count removed
- [x] `main(argv) -> int` catches `TodoError`, prints `error: <message>` to stderr, returns 1
- [x] Invalid ID input (e.g. `done abc`) gives an argparse error on stderr with exit code 2, no traceback
- [x] Add `if __name__ == "__main__": sys.exit(main())`

### 4. Tests (`tests/test_todo.py`)
- [x] Fixture that points `TODO_FILE` at a `tmp_path` file via `monkeypatch`
- [x] Test `add` prints sequential IDs and persists the todo
- [x] Test `list` output format for open and done todos
- [x] Test `done` marks the todo; `done` on a missing ID exits non-zero with a stderr message
- [x] Test `rm` deletes the todo; `rm` on a missing ID exits non-zero
- [x] Test IDs are not reused after `rm`
- [x] Test `clear` removes only done todos
- [x] Test a corrupt `todos.json` gives a clean error, not a traceback
- [x] Run `pytest tests/` and confirm everything passes

### 5. Documentation
- [x] Write `README.md`: requirements, usage examples for each command, how to run tests

## Notes
- Assumption: a single `todo.py` file is enough for this size; tests import it directly (add `tests/conftest.py` to put the project root on `sys.path` if needed).
- Assumption: monotonic IDs are tracked with a top-level `next_id` counter, so IDs aren't reused even when the highest-ID todo is removed. Each todo entry still matches the spec schema exactly.
- Assumption: the `TODO_FILE` env var exists only so tests can redirect storage; the default stays `./todos.json`.
- Assumption: `done` on an already-done todo succeeds and changes nothing (no error).
- Error exit codes: 1 for app errors (missing ID, corrupt file), 2 for argparse usage errors.
