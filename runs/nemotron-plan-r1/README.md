# Tiny CLI Todo Manager

A small command-line todo application built with Python 3.11+ and stdlib only.

## Usage

```bash
# Add a new todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo as done (by ID)
python todo.py done 1

# Remove a todo (by ID)
python todo.py rm 1

# Remove all done todos
python todo.py clear
```

## Notes

- IDs are monotonically increasing and never reused
- Todos are persisted to `./todos.json`
- Error messages are printed to stderr for invalid IDs