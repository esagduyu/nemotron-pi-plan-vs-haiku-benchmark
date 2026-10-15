"""Tests for the tiny CLI todo manager."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import todo


@pytest.fixture
def store_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point TODO_FILE at a temp file so tests don't pollute cwd."""
    path = tmp_path / "todos.json"
    monkeypatch.setenv("TODO_FILE", str(path))
    return path


def test_add_prints_sequential_ids_and_persists(store_file: Path) -> None:
    """Test add prints sequential IDs and persists the todo."""
    exit_code = todo.main(["add", "Buy milk"])
    assert exit_code == 0
    assert store_file.exists()

    data = json.loads(store_file.read_text())
    assert data["next_id"] == 2
    assert len(data["todos"]) == 1
    assert data["todos"][0] == {"id": 1, "title": "Buy milk", "done": False}

    # Second add gets next ID
    exit_code = todo.main(["add", "Walk the dog"])
    assert exit_code == 0
    data = json.loads(store_file.read_text())
    assert data["next_id"] == 3
    assert len(data["todos"]) == 2


def test_list_output_format(store_file: Path) -> None:
    """Test list output format for open and done todos."""
    todo.main(["add", "Task one"])
    todo.main(["add", "Task two"])
    data = todo.load()
    todo.mark_done(data, 1)
    todo.save(data=data)

    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        todo.main(["list"])
    output = f.getvalue()

    lines = output.strip().split("\n")
    assert len(lines) == 2
    assert lines[0] == "[1] [x] Task one"
    assert lines[1] == "[2] [·] Task two"


def test_done_marks_todo_and_missing_id_exits_nonzero(store_file: Path) -> None:
    """Test done marks the todo; done on a missing ID exits non-zero."""
    todo.main(["add", "Something"])

    exit_code = todo.main(["done", "1"])
    assert exit_code == 0
    data = todo.load()
    assert data["todos"][0]["done"] is True

    # Missing ID
    exit_code = todo.main(["done", "999"])
    assert exit_code == 1
    data = todo.load()
    # Should be unchanged
    assert data["todos"][0]["done"] is True


def test_rm_deletes_and_missing_id_exits_nonzero(store_file: Path) -> None:
    """Test rm deletes the todo; rm on a missing ID exits non-zero."""
    todo.main(["add", "To remove"])

    exit_code = todo.main(["rm", "1"])
    assert exit_code == 0
    data = todo.load()
    assert len(data["todos"]) == 0

    # Missing ID
    exit_code = todo.main(["rm", "1"])
    assert exit_code == 1


def test_ids_not_reused_after_rm(store_file: Path) -> None:
    """Test IDs are not reused after rm."""
    todo.main(["add", "First"])
    todo.main(["add", "Second"])
    todo.main(["add", "Third"])
    todo.main(["rm", "2"])  # Remove middle one

    data = todo.load()
    new_id = todo.add_todo(data, "Fourth")
    assert new_id == 4  # next_id was 4, not reused
    todo.save(data=data)

    ids = [t["id"] for t in data["todos"]]
    assert 2 not in ids
    assert 4 in ids


def test_clear_removes_only_done(store_file: Path) -> None:
    """Test clear removes only done todos."""
    todo.main(["add", "Open task"])
    todo.main(["add", "Done task"])
    todo.main(["done", "2"])

    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        exit_code = todo.main(["clear"])
    assert exit_code == 0
    output = f.getvalue().strip()
    assert "1" in output  # count

    data = todo.load()
    assert len(data["todos"]) == 1
    assert data["todos"][0]["title"] == "Open task"


def test_corrupt_store_gives_clean_error(store_file: Path) -> None:
    """Test a corrupt todos.json gives a clean error, not a traceback."""
    store_file.write_text("not valid json{{{")

    result = subprocess.run(
        [sys.executable, "-c", "import sys; import todo; sys.exit(todo.main(['list']))"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_subprocess_add_list(store_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI via subprocess to verify argparse integration."""
    monkeypatch.setenv("TODO_FILE", str(store_file))

    result = subprocess.run(
        [sys.executable, "todo.py", "add", "Subprocess todo"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Added todo 1" in result.stdout

    result = subprocess.run(
        [sys.executable, "todo.py", "list"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "[1] [·] Subprocess todo" in result.stdout
