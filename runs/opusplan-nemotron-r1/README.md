# Todo Manager

A tiny CLI todo manager written in Python 3.11+, stdlib only.

## Usage

```bash
python todo.py <command> [args]
```

### Commands

| Command | Description |
|---|---|
| `add <title>` | Add a new todo. Prints the new ID. |
| `list` | Print all todos as `[ID] [x|·] title`. `x` = done, `·` = open. |
| `done <id>` | Mark a todo done by ID. |
| `rm <id>` | Delete a todo by ID. |
| `clear` | Remove all done todos. |

### Examples

```bash
# Add a new todo
python todo.py add "Buy milk"
# Output: 1

# Add another todo
python todo.py add "Walk the dog"
# Output: 2

# List todos
python todo.py list
# Output:
# [1] [·] Buy milk
# [2] [x] Walk the dog

# Mark todo 1 as done
python todo.py done 1

# List again
python todo.py list
# Output:
# [1] [x] Buy milk
# [2] [·] Walk the dog

# Remove todo 2
python todo.py rm 2

# List remaining
python todo.py list
# Output:
# [1] [x] Buy milk

# Clear all done todos
python todo.py clear
```

### JSON persistence

Todos are stored in `./todos.json` relative to the current working directory. The file format is:

```json
{
  "next_id": 3,
  "todos": [
    {"id": 1, "title": "Buy milk", "done": true},
    {"id": 2, "title": "Walk the dog", "done": false}
  ]
}
```

IDs are monotonically increasing and never reused (even after `rm`).

### Running tests

```bash
pytest tests/
```

All tests use a temporary directory so they don't pollute the cwd.