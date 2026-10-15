"""Pytest tests for the todo CLI manager."""

import json
import os
import subprocess
import sys

import pytest

# The todo.py file is at the project root, next to this tests/ dir.
# We determine the project root relative to this test file.

TODO_FILE = "./todos.json"


def _get_todo_py():
    """Return absolute path to todo.py (sibling of this test file's dir)."""
    # __file__ -> /path/to/tests/test_todo.py
    # we want /path/to/todo.py
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)  # one level up from tests/
    return os.path.join(project_root, "todo.py")


TODO_PY = _get_todo_py()


def _run(args: list, tmpdir: os.PathLike) -> subprocess.CompletedProcess:
    """Run the todo CLI with *args*, chdir'd into *tmpdir* so ./todos.json lands there."""
    orig = os.getcwd()
    os.chdir(tmpdir)
    try:
        result = subprocess.run(
            [sys.executable, TODO_PY] + args,
            capture_output=True,
            text=True,
        )
    finally:
        os.chdir(orig)
    return result


# ── Fixture: tmp_path with a todos.json neighbour ──────────────────────────

@pytest.fixture(autouse=True)
def _tmp_todo_file(tmp_path):
    """Ensure ./todos.json is relative to tmp_path for each test."""
    yield


# ── Test: add ───────────────────────────────────────────────────────────────

def test_add_basic(tmp_path):
    """add prints the new ID and persists both todos."""
    result = _run(["add", "Buy milk"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    out = result.stdout.strip()
    assert out == "1", f"expected ID 1, got {out!r}"
    # Check persistence
    with open(os.path.join(tmp_path, "todos.json"), "r") as f:
        data = json.load(f)
    assert data["next_id"] == 2
    assert len(data["todos"]) == 1
    assert data["todos"][0]["title"] == "Buy milk"
    assert data["todos"][0]["done"] is False


def test_add_second_id(tmp_path):
    """Second add gets ID 2 (never reused after rm)."""
    # First add
    _run(["add", "First"], tmp_path)
    # Second add
    result = _run(["add", "Second"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    assert result.stdout.strip() == "2"


def test_list_empty(tmp_path):
    """list with no todos prints nothing and exits 0."""
    result = _run(["list"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    assert result.stdout == ""


def test_list_with_todos(tmp_path):
    """list output matches [ID] [x|·] title format."""
    _run(["add", "a"], tmp_path)
    _run(["add", "b"], tmp_path)
    # Mark first as done
    _run(["done", "1"], tmp_path)
    result = _run(["list"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    out_lines = result.stdout.strip().splitlines()
    # We should see: [1] [x] a and [2] [·] b (order may vary or be as inserted)
    assert any("[1] [x]" in l for l in out_lines), f"expected [1] [x] in {out_lines}"
    assert any("[2] [·]" in l for l in out_lines), f"expected [2] [·] in {out_lines}"


def test_done_marks(tmp_path):
    """done marks the todo done in the file; missing ID exits non-zero."""
    _run(["add", "wash"], tmp_path)
    # Mark done
    result = _run(["done", "1"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    # Verify via list
    result2 = _run(["list"], tmp_path)
    assert result2.returncode == 0, f"expected exit 0, got {result2.returncode}, stderr: {result2.stderr}"
    assert "[1] [x] wash" in result2.stdout, f"expected [1] [x] wash in {result2.stdout}"

    # done on missing ID
    result3 = _run(["done", "999"], tmp_path)
    assert result3.returncode != 0, f"expected non-zero exit, got {result3.returncode}"
    assert "error:" in result3.stderr


def test_rm(tmp_path):
    """rm removes the todo; subsequent add gets new higher ID (no reuse)."""
    _run(["add", "delete me"], tmp_path)
    # rm it
    result = _run(["rm", "1"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    # list should be empty
    result2 = _run(["list"], tmp_path)
    assert result2.returncode == 0, f"expected exit 0, got {result2.returncode}, stderr: {result2.stderr}"
    assert result2.stdout == ""
    # add again -> should get ID 2 (not reused ID 1)
    result3 = _run(["add", "new"], tmp_path)
    assert result3.returncode == 0, f"expected exit 0, got {result3.returncode}, stderr: {result3.stderr}"
    assert result3.stdout.strip() == "2"


def test_clear(tmp_path):
    """clear removes only done todos."""
    _run(["add", "a"], tmp_path)
    _run(["add", "b"], tmp_path)
    # Mark first done
    _run(["done", "1"], tmp_path)
    # clear done
    result = _run(["clear"], tmp_path)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}, stderr: {result.stderr}"
    # list should show only the open one
    result2 = _run(["list"], tmp_path)
    assert result2.returncode == 0, f"expected exit 0, got {result2.returncode}, stderr: {result2.stderr}"
    assert "[2] [·] b" in result2.stdout, f"expected [2] [·] b in {result2.stdout}"
    assert "[1] [x] a" not in result2.stdout


def test_invalid_id_done(tmp_path):
    """done abc exits non-zero without traceback."""
    result = _run(["done", "abc"], tmp_path)
    assert result.returncode != 0, f"expected non-zero exit, got {result.returncode}"
    assert "error:" in result.stderr


def test_corrupt_json_no_traceback(tmp_path):
    """Corrupt todos.json exits non-zero without a traceback."""
    fpath = os.path.join(tmp_path, "todos.json")
    # Write garbage
    with open(fpath, "w") as f:
        f.write("not valid json {{{")
    result = _run(["list"], tmp_path)
    assert result.returncode != 0, f"expected non-zero exit, got {result.returncode}"
    # No stack trace in stderr
    assert "Traceback" not in result.stderr


# ── End of tests ─────────────────────────────────────────────────────────────