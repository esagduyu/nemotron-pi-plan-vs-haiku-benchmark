# Tiny CLI Todo Manager

A minimal command-line todo app in Python (stdlib only).

## Usage

```
python todo.py add <title>      # Add a new todo
python todo.py list             # List all todos
python todo.py done <id>        # Mark a todo as done
python todo.py rm <id>          # Remove a todo
python todo.py clear            # Remove all done todos
```

## Example

```
$ python todo.py add "Buy groceries"
Added todo 1: Buy groceries

$ python todo.py add "Walk the dog"
Added todo 2: Walk the dog

$ python todo.py list
[1] [·] Buy groceries
[2] [·] Walk the dog

$ python todo.py done 1
Todo 1 marked done.

$ python todo.py list
[1] [x] Buy groceries
[2] [·] Walk the dog

$ python todo.py clear
Cleared 1 done todo(s).
```

## Testing

```
pytest tests/
```

## Notes

- Todos are persisted in `todos.json` in the same directory.
- IDs are monotonically increasing and never reused.
- Errors are printed to stderr with a non-zero exit code.
