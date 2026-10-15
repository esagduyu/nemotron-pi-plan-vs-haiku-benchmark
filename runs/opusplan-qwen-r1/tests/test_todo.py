"""Tests for the tiny todo CLI."""

import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout

import pytest

from todo import (
    TodoError,
    add_todo,
    clear_done,
    find_todo,
    format_todo,
    load,
    main,
    mark_done,
    remove_todo,
    save,
    STORE_PATH,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _chdir_tmp_path(monkeypatch, tmp_path):
    """Every test runs inside a temp directory so ./todos.json never leaks."""
    monkeypatch.chdir(tmp_path)


# ── add ──────────────────────────────────────────────────────────────────────

def test_add_prints_ids(monkeypatch, tmp_path):
    """Adding two todos prints IDs 1 then 2 and persists both."""
    result = main(["add", "first"])
    assert result == 0
    result = main(["add", "second"])
    assert result == 0

    data = json.loads((tmp_path / STORE_PATH).read_text())
    assert len(data["todos"]) == 2
    assert data["next_id"] == 3


def test_add_rejects_empty_title():
    """Empty / whitespace-only titles raise TodoError."""
    data = load()
    for title in ["", "   "]:
        with pytest.raises(TodoError, match="title must not be empty"):
            add_todo(data, title)


# ── list ─────────────────────────────────────────────────────────────────────

def test_list_format():
    """Output matches [ID] [·] title / [ID] [x] title format."""
    data = load()
    add_todo(data, "a")
    add_todo(data, "b")
    mark_done(data, 2)
    save(data)

    f = io.StringIO()
    with redirect_stdout(f):
        result = main(["list"])
    assert result == 0
    lines = f.getvalue().strip().splitlines()
    assert lines == ["[1] [·] a", "[2] [x] b"]


def test_list_empty_prints_nothing():
    """list with no todos prints nothing and exits 0."""
    f = io.StringIO()
    with redirect_stdout(f):
        result = main(["list"])
    assert result == 0
    assert f.getvalue().strip() == ""


# ── done ─────────────────────────────────────────────────────────────────────

def test_done_marks_todo():
    """Marking a todo done persists the change."""
    main(["add", "something"])
    main(["done", "1"])

    data = load()
    assert data["todos"][0]["done"] is True


def test_done_missing_id_exits_nonzero(capsys):
    """done on a missing ID exits non-zero with a stderr message."""
    result = main(["done", "99"])
    assert result == 1
    captured = capsys.readouterr()
    assert "no todo with id 99" in captured.err


def test_done_idempotent():
    """Marking an already-done todo succeeds silently."""
    main(["add", "idem"])
    main(["done", "1"])
    result = main(["done", "1"])
    assert result == 0


# ── rm ───────────────────────────────────────────────────────────────────────

def test_rm_removes_and_no_id_reuse():
    """rm removes the todo; subsequent add gets a higher ID."""
    main(["add", "keep"])
    main(["add", "bye"])
    main(["rm", "1"])

    data = load()
    assert len(data["todos"]) == 1
    assert data["todos"][0]["id"] == 2

    main(["add", "new"])
    data = load()
    assert data["next_id"] == 4  # IDs: 1, 2, 3 — never reused
    ids = [t["id"] for t in data["todos"]]
    assert 1 not in ids


def test_rm_missing_id_exits_nonzero(capsys):
    """rm on a missing ID exits non-zero."""
    result = main(["rm", "99"])
    assert result == 1
    captured = capsys.readouterr()
    assert "no todo with id 99" in captured.err


# ── clear ────────────────────────────────────────────────────────────────────

def test_clear_removes_only_done():
    """clear removes only done todos."""
    main(["add", "open"])
    main(["add", "done1"])
    main(["done", "2"])
    main(["add", "done2"])
    main(["done", "3"])

    main(["clear"])
    data = load()
    assert len(data["todos"]) == 1
    assert data["todos"][0]["title"] == "open"


# ── Invalid / corrupt ────────────────────────────────────────────────────────

def test_invalid_id_exits_nonzero(capsys):
    """done abc exits non-zero without traceback."""
    result = main(["done", "abc"])
    assert result == 1
    captured = capsys.readouterr()
    assert "invalid positive integer" in captured.err
    assert "Traceback" not in captured.err


def test_corrupt_json_exits_nonzero_no_traceback(tmp_path, capsys):
    """Corrupt todos.json exits non-zero without a traceback."""
    (tmp_path / STORE_PATH).write_text("{ broken json!!!")
    result = main(["list"])
    assert result == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "Traceback" not in captured.err


# ── Subprocess end-to-end ────────────────────────────────────────────────────

def test_subprocess_no_traceback_on_corrupt(tmp_path):
    """End-to-end: corrupt JSON produces clean error, no traceback."""
    # Copy todo.py into the temp dir so the subprocess can find it.
    import shutil
    shutil.copy(os.path.join(os.path.dirname(__file__), "..", "todo.py"),
                str(tmp_path / "todo.py"))

    store = tmp_path / STORE_PATH
    store.write_text("NOT JSON")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "todo.py", "list"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "error:" in result.stderr
