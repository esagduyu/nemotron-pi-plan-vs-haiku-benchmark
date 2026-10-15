# Tiny CLI Todo Manager

## Usage

```bash
# Add a new todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo as done (by ID)
python todo.py done 1

# Remove a todo by ID
python todo.py rm 1

# Remove all done todos
python todo.py clear
```

## Output Format

- `list` command shows todos as `[ID] [x|·] title`
  - `x` = done, `·` = open
- `add` command prints the new todo ID

## Notes

- IDs are monotonically increasing and never reused
- Todos are persisted in `todos.json`