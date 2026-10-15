# Tiny CLI Todo Manager

A small command-line todo manager using only Python stdlib.

## Usage

```bash
# Add a new todo
python todo.py add "Buy milk"

# List all todos
python todo.py list

# Mark a todo as done (by ID)
python todo.py done 1

# Delete a todo (by ID)
python todo.py rm 1

# Remove all done todos
python todo.py clear
```

## Notes

- IDs are monotonically increasing and never reused
- Todos are persisted in `./todos.json`
- Error messages are printed to stderr for invalid IDs