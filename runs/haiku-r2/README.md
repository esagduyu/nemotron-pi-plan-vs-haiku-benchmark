# todo

A tiny command-line todo manager. Python 3.11+, standard library only.

Todos are stored in `./todos.json` in the current directory (created on first use).

## Usage

```sh
python todo.py add buy milk        # prints the new ID, e.g. "1"
python todo.py add "walk the dog"
python todo.py list
# [1] [·] buy milk
# [2] [·] walk the dog

python todo.py done 1
python todo.py list
# [1] [x] buy milk
# [2] [·] walk the dog

python todo.py rm 2                # delete a todo
python todo.py clear               # remove all done todos
```

IDs only ever increase. Removing a todo never frees its ID for reuse.

Errors (unknown ID, empty title, corrupt file) print a message to stderr and exit with status 1.

## Tests

```sh
pip install pytest
pytest tests/ -q
```

The tests write to a temporary directory, so your `todos.json` is never touched.
