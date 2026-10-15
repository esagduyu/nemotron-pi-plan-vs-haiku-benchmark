# Toy project: tiny CLI todo manager (Python)

Build a small command-line todo app at the working directory.

## Functional requirements

- **Language**: Python 3.11+, stdlib only (except `pytest` for tests).
- **CLI** (use `argparse` with subcommands; entry: `python todo.py <command> [args]`):
  - `add <title>` — add a new todo. Prints the new ID.
  - `list` — print all todos as `[ID] [x|·] title`. `x` = done, `·` = open.
  - `done <id>` — mark a todo done by ID.
  - `rm <id>` — delete a todo by ID.
  - `clear` — remove all done todos.
- **Persistence**: JSON file at `./todos.json` (created if missing).
- **Schema**: each todo has integer `id`, string `title`, boolean `done`.
- **IDs**: monotonically increasing — never reused even after `rm`.
- **Errors**: missing/invalid IDs should print a clear error to stderr and exit non-zero. Don't crash with a stack trace.
- **Tests**: at least 4 pytest tests in `tests/test_todo.py` covering add, list, done, rm. Use a temp directory for the JSON file (don't pollute the cwd during tests).
- **README.md**: brief, with usage examples.

## Layout

You choose whether to keep it one file or split. Reasonable splits welcome.

## Quality bar

- No external runtime deps.
- No silent failures.
- Tests should pass with `pytest tests/`.
- Code should be readable — type hints encouraged but not required.
