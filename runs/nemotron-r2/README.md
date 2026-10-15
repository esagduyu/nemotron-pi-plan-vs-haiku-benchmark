# Tiny CLI Todo Manager

A minimal command-line todo manager using only Python stdlib.

## Usage

```bash
# Add a new todo
python todo.py add "Buy milk"

# List all todos
python todo.py list

# Mark a todo done (by ID)
python todo.py done 1

# Remove a todo by ID
python todo.py rm 1

# Clear all done todos
python todo.py clear
```

## Persistence

Todos are stored in `./todos.json`. The file is created automatically on first use.

## ID Behavior

- IDs are integers, monotonically increasing, and never reused (even after `rm`).
- Example: after adding, removing, and adding again, IDs continue from the highest ever used.