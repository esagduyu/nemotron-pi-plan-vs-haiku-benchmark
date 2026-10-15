# Tiny CLI Todo Manager

A small command-line todo manager using only Python stdlib.

## Usage

```bash
# Add a new todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo as done
python todo.py done 1

# Delete a todo
python todo.py rm 1

# Remove all completed todos
python todo.py clear
```

## Notes

- Todos are persisted in `./todos.json`
- IDs are monotonically increasing and never reused
- Error messages are printed to stderr with non-zero exit code for invalid IDs
- Empty titles are rejected