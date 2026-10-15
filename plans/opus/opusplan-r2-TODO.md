# TODO

## Goal
Build a stdlib-only Python CLI todo manager (`python todo.py <command>`) with JSON persistence, never-reused IDs, clean error handling, pytest tests, and a README.

## Tasks

### 1. Storage layer (`todo.py`)
- [ ] Define the on-disk format: `{"next_id": int, "todos": [{"id": int, "title": str, "done": bool}, ...]}`
- [ ] Implement `load(path) -> dict` that returns an empty store (`next_id: 1`, `todos: []`) when the file is missing
- [ ] Make `load` raise a clear `TodoError` when the file contains invalid JSON or the wrong structure
- [ ] Implement `save(path, data)` that writes atomically (temp file + `os.replace`)
- [ ] Make the store path default to `./todos.json`, overridable via `TODO_FILE` env var (used by tests)

### 2. Core operations (`todo.py`)
- [ ] `add_todo(data, title) -> int`: assigns `next_id`, increments it, returns the new ID; rejects empty/whitespace titles
- [ ] `mark_done(data, id)`: raises `TodoError` if ID not found
- [ ] `remove_todo(data, id)`: raises `TodoError` if ID not found; does not decrement `next_id`
- [ ] `clear_done(data) -> int`: removes done todos, returns count removed
- [ ] `format_todo(todo) -> str`: returns `[ID] [x|·] title`

### 3. CLI (`todo.py`)
- [ ] Build an `argparse` parser with subcommands `add <title>`, `list`, `done <id>`, `rm <id>`, `clear`; `id` parsed with `type=int`
- [ ] `add` prints the new ID; `list` prints one formatted line per todo (prints nothing when empty); `clear` prints count removed
- [ ] `main(argv) -> int` catches `TodoError`, prints `error: <message>` to stderr, returns 1
- [ ] Invalid ID input (e.g. `done abc`) gives an argparse error on stderr with exit code 2, no traceback
- [ ] Add `if __name__ == "__main__": sys.exit(main())`

### 4. Tests (`tests/test_todo.py`)
- [ ] Fixture that points `TODO_FILE` at a `tmp_path` file via `monkeypatch`
- [ ] Test `add` prints sequential IDs and persists the todo
- [ ] Test `list` output format for open and done todos
- [ ] Test `done` marks the todo; `done` on a missing ID exits non-zero with a stderr message
- [ ] Test `rm` deletes the todo; `rm` on a missing ID exits non-zero
- [ ] Test IDs are not reused after `rm`
- [ ] Test `clear` removes only done todos
- [ ] Test a corrupt `todos.json` gives a clean error, not a traceback
- [ ] Run `pytest tests/` and confirm everything passes

### 5. Documentation
- [ ] Write `README.md`: requirements, usage examples for each command, how to run tests

## Notes
- Assumption: a single `todo.py` file is enough for this size; tests import it directly (add `tests/conftest.py` to put the project root on `sys.path` if needed).
- Assumption: monotonic IDs are tracked with a top-level `next_id` counter, so IDs aren't reused even when the highest-ID todo is removed. Each todo entry still matches the spec schema exactly.
- Assumption: the `TODO_FILE` env var exists only so tests can redirect storage; the default stays `./todos.json`.
- Assumption: `done` on an already-done todo succeeds and changes nothing (no error).
- Error exit codes: 1 for app errors (missing ID, corrupt file), 2 for argparse usage errors.
