# Tiny CLI Todo Manager

A small command-line todo manager built with Python 3.11+ and stdlib only.

## Usage

```bash
# Add a new todo
python todo.py add "Buy milk"
# Output: 1

# List all todos
python todo.py list
# Output: [1] [·] Buy milk

# Mark a todo as done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Clear all done todos
python todo.py clear
```

## Commands

| Command | Description |
|---------|-------------|
| `add <title>` | Add a new todo with the given title. Prints the new ID. |
| `list` | Print all todos. `x` = done, `·` = open. |
| `done <id>` | Mark a todo as done by ID. |
| `rm <id>` | Delete a todo by ID. |
| `clear` | Remove all done todos. |

## Persistence

Todos are stored in `todos.json` (created automatically if missing). IDs are monotonically increasing and never reused.

## Tests

Run the test suite with:
```bash
pytest tests/
```

## Requirements

- Python 3.11+
- stdlib only (except `pytest` for tests)
- No external runtime dependencies