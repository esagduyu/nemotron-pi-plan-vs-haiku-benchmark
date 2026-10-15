# Tiny CLI Todo Manager

A small command-line todo application built with Python 3.11+ stdlib.

## Usage

```bash
# Add a new todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Mark a todo as done
python todo.py done 1

# Remove a todo
python todo.py rm 1

# Clear all done todos
python todo.py clear
```

## Output Format

`[ID] [x|·] title`
- `x` = done
- `·` = open

## Persistence

Todos are saved to `todos.json` in the current directory.