# tiny CLI todo manager

A minimal, stdlib-only Python CLI todo app with JSON persistence.

## Requirements

- Python 3.11+

## Usage

```
python todo.py add <title>      # Add a new todo (prints the new ID)
python todo.py list             # List all todos
python todo.py done <id>        # Mark a todo as done
python todo.py rm <id>          # Remove a todo by ID
python todo.py clear            # Remove all done todos
```

### Examples

```
$ python todo.py add "Buy milk"
Added todo 1
$ python todo.py add "Walk the dog"
Added todo 2
$ python todo.py list
[1] [·] Buy milk
[2] [·] Walk the dog
$ python todo.py done 1
$ python todo.py list
[1] [x] Buy milk
[2] [·] Walk the dog
$ python todo.py rm 2
$ python todo.py list
[1] [x] Buy milk
$ python todo.py add "New task"
Added todo 3
```

## Persistence

Todos are stored in `./todos.json` in the current working directory:

```json
{
  "next_id": 4,
  "todos": [
    {"id": 1, "title": "Buy milk", "done": true}
  ]
}
```

## Tests

```
pytest tests/
```

Requires `pytest` (test-only dependency).
