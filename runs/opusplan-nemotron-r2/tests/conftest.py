"""conftest.py — redirect TODO_FILE to a temp file for tests."""

import os
import sys

import pytest

# Ensure the project root (where todo.py lives) is on sys.path
# so that `import todo` works regardless of cwd.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from todo import _default_path


@pytest.fixture(autouse=True)
def redirect_todo_file(tmp_path, monkeypatch):
    """Point TODO_FILE at a temp file for every test."""
    p = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(p))
