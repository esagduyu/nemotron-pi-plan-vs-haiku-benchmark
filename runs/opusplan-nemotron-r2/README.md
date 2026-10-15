# Tiny CLI Todo Manager

A small command-line todo application built with Python 3.11+ and stdlib only.

## Installation

No external dependencies required. Simply ensure you have Python 3.11+ installed.

## Usage

Run with `python todo.py <command> [args]`:

### Commands

- `add <title>` — Add a new todo. Prints the new ID.
- `list` — Print all todos. `x` = done, `·` = open.
- `done <id>` — Mark a todo done by ID.
- `rm <id>` — Delete a todo by ID.
- `clear` — Remove all done todos. Prints count removed.

### Examples

```bash
# Add a new todo
python todo.py add "Buy milk"
# Output: 1

# List all todos
python todo.py list
# Output:
# [1] [·] Buy milk

# Mark todo 1 as done
python todo.py done 1

# List again
python todo.py list
# Output:
# [1] [x] Buy milk

# Remove a todo
python todo.py rm 1

# Clear all done todos
python todo.py add "Task 1"
python todo.py add "Task 2"
python todo.py done 2
python todo.py clear
# Output: 1
```

## Persistence

Todos are stored in `./todos.json` (created automatically if missing). IDs are monotonically increasing and never reused.

## Running Tests

```bash
pytest tests/
```

Tests cover: add, list, done, rm, ID non-reuse, clear, and corrupt file handling.

## Error Handling

- Missing/invalid IDs print `error: <message>` to stderr and exit non-zero
- Invalid input (e.g., `done abc`) gives argparse error with exit code 2
- Corrupt `todos.json` gives a clean error without stack traces